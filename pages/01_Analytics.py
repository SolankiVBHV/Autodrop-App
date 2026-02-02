"""
Analytics Dashboard - Metrics and visualizations for Autodrop
"""

import os
# Import config loader for Streamlit secrets + .env support
import sys
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
import streamlit as st
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import get_db_config

load_dotenv()

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

@st.cache_data(ttl=3600)
def fetch_metric_data(query: str):
    """Fetch data with caching (1 hour TTL)"""
    conn = None
    try:
        db_config = get_db_config()
        conn = psycopg2.connect(
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"]
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            data = cur.fetchall()
            return data
            
    except psycopg2.Error as e:
        st.error(f"Database query failed: {e}")
        return None
    finally:
        if conn and not conn.closed:
            conn.close()

def get_date_range(period: str) -> tuple:
    """Calculate date range based on period selection"""
    end_date = datetime.now()
    
    if period == "Last 7 days":
        start_date = end_date - timedelta(days=7)
    elif period == "Last 30 days":
        start_date = end_date - timedelta(days=30)
    elif period == "Last 90 days":
        start_date = end_date - timedelta(days=90)
    elif period == "Last 6 months":
        start_date = end_date - timedelta(days=180)
    elif period == "Last 12 months":
        start_date = end_date - timedelta(days=365)
    else:  # All-time
        start_date = datetime(2020, 1, 1)
    
    return start_date, end_date

# Title
st.title("Analytics Dashboard")
st.markdown("---")

# Sidebar - Time range selector
with st.sidebar:
    st.header("Filters")
    time_period = st.selectbox(
        "Time Period",
        ["Last 7 days", "Last 30 days", "Last 90 days", "Last 6 months", "Last 12 months", "All-time"],
        index=1
    )
    start_date, end_date = get_date_range(time_period)
    st.text(f"Range: {start_date.date()} to {end_date.date()}")

# SECTION 1: Key Performance Indicators
st.header("Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

# Query: Total videos generated
query_generated = f"""
SELECT COUNT(*) as total_generated 
FROM video_generations 
WHERE status = 'completed' 
AND created_at >= '{start_date.date()}'::date
AND created_at < '{end_date.date()}'::date + interval '1 day';
"""

# Query: Total videos uploaded
query_uploaded = f"""
SELECT COUNT(DISTINCT video_generation_id) as total_uploaded 
FROM video_uploads 
WHERE upload_status = 'completed'
AND created_at >= '{start_date.date()}'::date
AND created_at < '{end_date.date()}'::date + interval '1 day';
"""

# Query: Videos awaiting review
query_pending = f"""
SELECT COUNT(*) as pending_review 
FROM video_generations 
WHERE reviewed_at IS NULL
AND review_status IS NULL
AND created_at >= '{start_date.date()}'::date
AND created_at < '{end_date.date()}'::date + interval '1 day';
"""

# Query: Approval rate
query_approval = f"""
SELECT 
  COUNT(CASE WHEN review_status = 'approved' THEN 1 END)::float / 
  NULLIF(COUNT(CASE WHEN review_status IS NOT NULL THEN 1 END), 0) * 100 as approval_rate
FROM video_generations 
WHERE created_at >= '{start_date.date()}'::date
AND created_at < '{end_date.date()}'::date + interval '1 day';
"""

# Query: Overall pipeline conversion (uploaded / ingested)
query_upload_rate = f"""
WITH stats AS (
  SELECT 
    (SELECT COUNT(DISTINCT video_generation_id) FROM video_uploads WHERE upload_status = 'completed' AND created_at >= '{start_date.date()}'::date AND created_at < '{end_date.date()}'::date + interval '1 day') as uploaded_count,
    (SELECT COUNT(*) FROM news WHERE created_at >= '{start_date.date()}'::date AND created_at < '{end_date.date()}'::date + interval '1 day') as ingested_count
)
SELECT ROUND(100.0 * uploaded_count / NULLIF(ingested_count, 0), 1) as pipeline_conversion_rate
FROM stats;
"""

# Execute queries
try:
    data_generated = fetch_metric_data(query_generated)
    data_uploaded = fetch_metric_data(query_uploaded)
    data_pending = fetch_metric_data(query_pending)
    data_approval = fetch_metric_data(query_approval)
    data_upload_rate = fetch_metric_data(query_upload_rate)
    
    with col1:
        generated = data_generated[0]['total_generated'] if data_generated else 0
        st.metric("Generated", generated)
    
    with col2:
        uploaded = data_uploaded[0]['total_uploaded'] if data_uploaded else 0
        st.metric("Uploaded", uploaded)
    
    with col3:
        pending = data_pending[0]['pending_review'] if data_pending else 0
        st.metric("Pending Review", pending)
    
    with col4:
        approval = data_approval[0]['approval_rate'] if data_approval and data_approval[0]['approval_rate'] else 0
        st.metric("Approval Rate", f"{approval:.1f}%" if approval else "0%")
    
    with col5:
        conversion_rate = data_upload_rate[0]['pipeline_conversion_rate'] if data_upload_rate and data_upload_rate[0]['pipeline_conversion_rate'] else 0
        st.metric("Pipeline Conversion", f"{conversion_rate:.1f}%" if conversion_rate else "0%")
except Exception as e:
    st.warning(f"Error loading KPI metrics: {e}")

st.markdown("---")

# SECTION 2: Upload Timeline
st.header("Upload Timeline")

query_timeline = f"""
SELECT 
  DATE(created_at)::text as upload_date,
  COUNT(DISTINCT video_generation_id) as videos_uploaded
FROM video_uploads 
WHERE upload_status = 'completed'
AND created_at >= '{start_date.date()}'::date
AND created_at < '{end_date.date()}'::date + interval '1 day'
GROUP BY DATE(created_at)
ORDER BY upload_date;
"""

try:
    timeline_data = fetch_metric_data(query_timeline)
    if timeline_data and len(timeline_data) > 0:
        df = pd.DataFrame(timeline_data)
        df['upload_date'] = pd.to_datetime(df['upload_date'])
        df = df.sort_values('upload_date')
        
        fig = px.area(df, x='upload_date', y='videos_uploaded',
                     title="Daily Video Uploads",
                     labels={'upload_date': 'Date', 'videos_uploaded': 'Videos Uploaded'},
                     color_discrete_sequence=['#9D4EDD'])
        fig.update_traces(fillcolor='rgba(157, 78, 221, 0.3)', line=dict(color='#9D4EDD', width=3))
        fig.update_layout(
            hovermode='x unified',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No upload data available for selected period")
except Exception as e:
    st.warning(f"Error loading timeline: {e}")

st.markdown("---")

# SECTION 3: Pipeline Funnel
st.header("Pipeline Funnel")
col_funnel1, col_funnel2 = st.columns(2)

with col_funnel1:
    query_funnel = f"""
    WITH funnel_data AS (
      SELECT 1 as stage_order, 'Ingested' as stage, COUNT(DISTINCT id) as count
      FROM news
      WHERE created_at >= '{start_date.date()}'::date
      AND created_at < '{end_date.date()}'::date + interval '1 day'
      UNION ALL
      SELECT 2, 'Summarized', COUNT(DISTINCT article_id)
      FROM article_summaries
      WHERE created_at >= '{start_date.date()}'::date
      AND created_at < '{end_date.date()}'::date + interval '1 day'
      UNION ALL
      SELECT 3, 'Audio Generated', COUNT(DISTINCT article_id)
      FROM audio_transcripts
      WHERE created_at >= '{start_date.date()}'::date
      AND created_at < '{end_date.date()}'::date + interval '1 day'
      UNION ALL
      SELECT 4, 'Video Generated', COUNT(DISTINCT id)
      FROM video_generations
      WHERE status = 'completed'
      AND created_at >= '{start_date.date()}'::date
      AND created_at < '{end_date.date()}'::date + interval '1 day'
      UNION ALL
      SELECT 5, 'Approved', COUNT(DISTINCT id)
      FROM video_generations
      WHERE review_status = 'approved'
      AND created_at >= '{start_date.date()}'::date
      AND created_at < '{end_date.date()}'::date + interval '1 day'
      UNION ALL
      SELECT 6, 'Uploaded', COUNT(DISTINCT video_generation_id)
      FROM video_uploads
      WHERE upload_status = 'completed'
      AND created_at >= '{start_date.date()}'::date
      AND created_at < '{end_date.date()}'::date + interval '1 day'
    )
    SELECT stage, count FROM funnel_data ORDER BY stage_order;
    """
    
    try:
        funnel_data = fetch_metric_data(query_funnel)
        if funnel_data and len(funnel_data) > 0:
            df_funnel = pd.DataFrame(funnel_data)
            # Sort by stage_order to get correct sequence
            df_funnel = df_funnel.sort_values('stage', key=lambda x: x.map({'Ingested': 1, 'Summarized': 2, 'Audio Generated': 3, 'Video Generated': 4, 'Approved': 5, 'Uploaded': 6}))
            
            fig = go.Figure(go.Funnel(
                y = df_funnel['stage'],
                x = df_funnel['count'],
                textposition = "inside",
                textinfo = "value+percent initial",
                marker=dict(
                    color=df_funnel['count'],
                    colorscale='Purples',
                    line=dict(color='rgba(157, 78, 221, 0.8)', width=1)
                )
            ))
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No pipeline data available")
    except Exception as e:
        st.warning(f"Error loading funnel: {e}")

with col_funnel2:
    st.subheader("Processing Time Analysis")
    
    # Query 1: Automated processing time (news to video completion, before review)
    query_processing_time = f"""
    SELECT 
      ROUND(AVG(EXTRACT(EPOCH FROM (vg.completed_at - n.created_at)) / 3600)::numeric, 2) as avg_hours,
      ROUND(MIN(EXTRACT(EPOCH FROM (vg.completed_at - n.created_at)) / 3600)::numeric, 2) as min_hours,
      ROUND(MAX(EXTRACT(EPOCH FROM (vg.completed_at - n.created_at)) / 3600)::numeric, 2) as max_hours
    FROM video_generations vg
    JOIN news n ON vg.article_id = n.id
    WHERE vg.status = 'completed'
    AND vg.completed_at IS NOT NULL
    AND vg.created_at >= '{start_date.date()}'::date
    AND vg.created_at < '{end_date.date()}'::date + interval '1 day';
    """
    
    # Query 2: Total turnaround including review (news to upload)
    query_turnaround_time = f"""
    SELECT 
      ROUND(AVG(EXTRACT(EPOCH FROM (vu.created_at - n.created_at)) / 3600)::numeric, 2) as avg_hours,
      ROUND(MIN(EXTRACT(EPOCH FROM (vu.created_at - n.created_at)) / 3600)::numeric, 2) as min_hours,
      ROUND(MAX(EXTRACT(EPOCH FROM (vu.created_at - n.created_at)) / 3600)::numeric, 2) as max_hours
    FROM video_generations vg
    JOIN news n ON vg.article_id = n.id
    JOIN video_uploads vu ON vg.id = vu.video_generation_id
    WHERE vu.upload_status = 'completed'
    AND vu.created_at >= '{start_date.date()}'::date
    AND vu.created_at < '{end_date.date()}'::date + interval '1 day';
    """
    
    try:
        processing_data = fetch_metric_data(query_processing_time)
        turnaround_data = fetch_metric_data(query_turnaround_time)
        
        if processing_data and processing_data[0]['avg_hours']:
            avg_proc = processing_data[0]['avg_hours']
            min_proc = processing_data[0]['min_hours']
            max_proc = processing_data[0]['max_hours']
            
            st.metric("Processing Time (Excl. Review)", f"{avg_proc:.1f}h")
            st.caption(f"News → Video Completion | Range: {min_proc:.1f}h - {max_proc:.1f}h")
        
        st.markdown("")
        
        if turnaround_data and turnaround_data[0]['avg_hours']:
            avg_turn = turnaround_data[0]['avg_hours']
            min_turn = turnaround_data[0]['min_hours']
            max_turn = turnaround_data[0]['max_hours']
            
            st.metric("Total Turnaround (Incl. Review)", f"{avg_turn:.1f}h")
            st.caption(f"News → Upload | Range: {min_turn:.1f}h - {max_turn:.1f}h")
        
        if not processing_data and not turnaround_data:
            st.info("No processing time data available")
    except Exception as e:
        st.warning(f"Error loading processing time: {e}")

st.markdown("---")

# SECTION 4: Channel Performance
st.header("Channel Metrics")

query_channels = f"""
SELECT 
  c.name as channel_name,
  COUNT(*) as total_uploads,
  SUM(CASE WHEN u.upload_status = 'completed' THEN 1 ELSE 0 END) as successful,
  ROUND(100.0 * SUM(CASE WHEN u.upload_status = 'completed' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) as success_rate,
  u.platform
FROM video_uploads u
LEFT JOIN channels c ON u.channel_id = c.id
WHERE u.created_at >= '{start_date.date()}'::date
AND u.created_at < '{end_date.date()}'::date + interval '1 day'
GROUP BY c.name, u.platform
ORDER BY total_uploads DESC;
"""

try:
    channel_data = fetch_metric_data(query_channels)
    if channel_data and len(channel_data) > 0:
        df_channels = pd.DataFrame(channel_data)
        
        col_ch1, col_ch2 = st.columns(2)
        
        with col_ch1:
            fig_uploads = px.bar(df_channels.sort_values('total_uploads', ascending=True), 
                                x='total_uploads', y='channel_name',
                                orientation='h',
                                title="Uploads by Channel",
                                labels={'channel_name': 'Channel', 'total_uploads': 'Upload Count'},
                                color='total_uploads',
                                color_continuous_scale='Purples')
            fig_uploads.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            )
            st.plotly_chart(fig_uploads, width='stretch')
        
        with col_ch2:
            fig_success = px.bar(df_channels.sort_values('success_rate', ascending=True),
                                x='success_rate', y='channel_name',
                                orientation='h',
                                title="Upload Success Rate by Channel",
                                labels={'channel_name': 'Channel', 'success_rate': 'Success Rate (%)'},
                                color='success_rate',
                                color_continuous_scale='Blues')
            fig_success.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            )
            st.plotly_chart(fig_success, width='stretch')
    else:
        st.info("No channel data available")
except Exception as e:
    st.warning(f"Error loading channel data: {e}")

st.markdown("---")

# SECTION 5: Content Breakdown
st.header("Content Analysis")

col_content1, col_content2 = st.columns(2)

with col_content1:
    query_categories = f"""
    SELECT category, COUNT(*) as count
    FROM news
    WHERE created_at >= '{start_date.date()}'::date
    AND created_at < '{end_date.date()}'::date + interval '1 day'
    GROUP BY category
    ORDER BY count DESC;
    """
    
    try:
        category_data = fetch_metric_data(query_categories)
        if category_data and len(category_data) > 0:
            df_categories = pd.DataFrame(category_data)
            fig = px.pie(df_categories, values='count', names='category',
                        title="Content by Category")
            fig.update_layout(height=400)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No category data available")
    except Exception as e:
        st.warning(f"Error loading categories: {e}")

with col_content2:
    query_sources = f"""
    SELECT source_name, COUNT(*) as count
    FROM news
    WHERE created_at >= '{start_date.date()}'::date
    AND created_at < '{end_date.date()}'::date + interval '1 day'
    GROUP BY source_name
    ORDER BY count DESC
    LIMIT 10;
    """
    
    try:
        source_data = fetch_metric_data(query_sources)
        if source_data and len(source_data) > 0:
            df_sources = pd.DataFrame(source_data)
            df_sources = df_sources.sort_values('count', ascending=True)
            fig = px.bar(df_sources, y='source_name', x='count',
                        orientation='h',
                        title="Top 10 News Sources",
                        labels={'source_name': 'Source', 'count': 'Articles'},
                        color='count',
                        color_continuous_scale='Viridis')
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)'),
                coloraxis_colorbar=dict(title="Count")
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No source data available")
    except Exception as e:
        st.warning(f"Error loading sources: {e}")

st.markdown("---")

# Footer
st.markdown("""
<small>Last updated: Data refreshes every hour. For detailed documentation, see [Metrics & Visualizations](./docs/METRICS_AND_VISUALIZATIONS.md)</small>
""", unsafe_allow_html=True)
