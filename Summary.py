"""
Autodrop App - Main Dashboard
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Summary",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main dashboard
st.title("🎯 Autodrop Dashboard")

st.markdown("""
Welcome to **Autodrop** - A video generator that converts NEWS to YouTube Shorts.

This dashboard provides comprehensive insights into Autodrop, a video generation pipeline, from content ingestion to distribution across multiple channels.
""")

st.markdown("---")

# Overview section - Content
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("📊 Analytics")
    st.markdown("""
    View comprehensive metrics and visualizations:
    - Key performance indicators
    - Processing time analysis
    - Pipeline funnel visualization
    - Channel performance metrics
    - Content breakdown and analysis
    """)

with col2:
    st.subheader("🎬 Videos")
    st.markdown("""
    Play Shorts directly from your channels:
    - Inline playback
    """)

with col3:
    st.subheader("🏗️ Architecture Overview")
    st.markdown("""
    Understand the system architecture:
    - Pipeline components and flow
    - Module responsibilities
    - Data flow diagrams
    - Integration points
    - System design patterns
    """)

with col4:
    st.subheader("📚 Detailed Architecture")
    st.markdown("""
    Deep dive into system design:
    - Pre-approval pipeline
    - Post-approval pipeline
    - Scheduled jobs
    - Database schema
    - Component interactions
    """)

# Overview section - Buttons (aligned in separate row)
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)

with btn_col1:
    if st.button("Go to Analytics →", width='stretch'):
        st.switch_page("pages/01_Analytics.py")

with btn_col2:
    if st.button("Go to Videos →", width='stretch'):
        st.switch_page("pages/02_Videos.py")

with btn_col3:
    if st.button("View Quick Reference →", width='stretch'):
        st.switch_page("pages/10_Architecture_Overview.py")

with btn_col4:
    if st.button("View Full Documentation →", width='stretch'):
        st.switch_page("pages/11_Architecture_Deepdive.py")

st.markdown("---")

# Quick stats section
st.subheader("📈 Quick Start")
st.markdown("""
**Getting Started:**
1. Navigate to **Analytics** to see real-time performance metrics
2. Open **Videos** to play Shorts from your channels
3. Check **Architecture Overview** to quickly glance the architecture
4. Visit **Architecture Deepdive** to view detailed explanations of each component
**Key Metrics to Monitor:**
- **Pipeline Conversion Rate** - Percentage of articles that make it through the complete pipeline
- **Processing Time** - How long articles take to become videos
- **Approval Rate** - Success rate of video reviews
- **Upload Success** - Reliability of video distribution
""")

st.info("💡 Use the sidebar to navigate between different sections of the dashboard.")

