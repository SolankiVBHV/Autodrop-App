# Metrics and Visualizations

## Core Metrics (From Todo)

### 1. Total Videos Generated and Uploaded
- **Query**: `COUNT(video_generations WHERE status = 'completed')` + `COUNT(video_uploads WHERE upload_status = 'completed')`
- **Visualization**: Large KPI cards with delta comparison (vs. previous period)
- **Time Range**: All-time, Last 7 days, Last 30 days, Last 6 months, Last 12 months

### 2. Upload Timeline
- **Query**: `SELECT DATE(uploaded_at), COUNT(*) FROM video_uploads WHERE upload_status = 'completed' GROUP BY DATE(uploaded_at)`
- **Visualization**: Line chart with date range selector dropdown
- **Breakdown**: Optional filtering by channel and platform

---

## Recommended Additional Metrics

### Pipeline Efficiency Metrics

**1. Generation Pipeline Funnel**
- **Metrics to track**:
  - News ingested
  - Articles deduplicated (removed)
  - Summaries generated
  - Audio generated
  - Videos generated
  - Videos approved for upload
  - Videos successfully uploaded
- **Visualization**: Funnel chart showing drop-off at each stage
- **Use case**: Identify bottlenecks in the pipeline

**2. Approval Rate**
- **Query**: `(COUNT(review_status = 'approved') / COUNT(review_status IS NOT NULL)) * 100`
- **Visualization**: Gauge chart (0-100%)
- **Breakdown**: By channel and by content category

**3. Processing Time Distribution**
- **Metrics**:
  - Average time: News → Summary (script generation)
  - Average time: Summary → Audio (TTS)
  - Average time: Audio → Video (video assembly)
  - Total end-to-end time
- **Visualization**: Box plots showing median, quartiles, outliers
- **Use case**: Identify performance regressions

---

### Channel Performance Metrics

**1. Upload Distribution by Channel**
- **Query**: `SELECT channel_name, COUNT(*) FROM video_uploads GROUP BY channel_name`
- **Visualization**: Horizontal bar chart (sorted by count)
- **Breakdown**: Stacked by upload_status (completed, pending, failed)

**2. Upload Success Rate by Channel**
- **Query**: `(COUNT(upload_status = 'completed') / COUNT(*)) * 100 per channel`
- **Visualization**: Bar chart with % labels
- **Use case**: Identify problematic channels

**3. Platform Breakdown**
- **Query**: `SELECT platform, COUNT(*) FROM video_uploads GROUP BY platform`
- **Visualization**: Pie chart or donut chart
- **Breakdown**: YouTube vs Instagram vs TikTok vs Others

**4. Daily Upload Capacity Utilization**
- **Query**: `(SUM(daily_uploads) / SUM(daily_upload_limit)) * 100 per channel`
- **Visualization**: Stacked bar chart showing used vs available capacity
- **Use case**: Capacity planning

---

### Content Quality Metrics

**1. Content Category Distribution**
- **Query**: `SELECT category, COUNT(*) FROM news WHERE created_at > ? GROUP BY category`
- **Visualization**: Bar chart (sorted by count)
- **Breakdown**: By time period (daily, weekly)

**2. Engagement Signals (Pre-Upload)**
- **Metrics**:
  - Average sentiment score (from AI analysis)
  - Distribution of engagement styles (breaking, celebrity, sports, tech, etc.)
  - Key points per summary
- **Visualization**: 
  - Histogram: Sentiment distribution
  - Bar chart: Engagement style breakdown
  - Line chart: Average sentiment over time

**3. Hashtag Performance**
- **Query**: Top hashtags used in uploaded videos, their frequency
- **Visualization**: Tag cloud (size = frequency)
- **Use case**: Trend detection and SEO optimization

**4. Source Distribution**
- **Query**: `SELECT source_name, COUNT(*) FROM news GROUP BY source_name`
- **Visualization**: Bar chart
- **Use case**: Identify best-performing news sources

---

### Asset Usage and Cost Metrics

**1. Media Asset Reuse Rate**
- **Query**: Count how many videos reused the same image/asset
- **Metric**: `(Total asset uses / Total assets) * 100`
- **Visualization**: Gauge chart
- **Use case**: Cost optimization (storage cleanup deletes assets with <2 reuses)

**2. Asset Source Breakdown**
- **Query**: `SELECT source_api, COUNT(*) FROM media_assets GROUP BY source_api`
- **Visualization**: Pie chart
- **Use case**: Understand diversity of asset sources

**3. TTS Provider Usage**
- **Query**: Track which TTS providers were used (Kokoro vs Coqui vs Azure)
- **Visualization**: Stacked area chart over time
- **Use case**: Monitor fallback chain utilization

**4. LLM Provider Rotation**
- **Query**: Track API calls by provider (Gemini, Groq, Ollama)
- **Visualization**: Stacked bar chart
- **Use case**: Monitor quota utilization balance

---

### Engagement and Performance Metrics

**1. Video Performance (If YouTube API is accessible)**
- **Metrics**:
  - Total views across all videos
  - Average views per video
  - Click-through rate (if available)
  - Like-to-view ratio
  - Comment engagement rate
- **Visualization**:
  - Line chart: Cumulative views over time
  - Scatter plot: Views vs Engagement (likes/comments)

**2. Video Review Efficiency**
- **Metrics**:
  - Average review time (created_at → reviewed_at)
  - Review approval rate vs rejection rate
- **Visualization**: 
  - Line chart: Review lag over time
  - Pie chart: Approval vs rejection rates

**3. Upload Error Tracking**
- **Query**: Failed uploads grouped by error_message and channel
- **Visualization**: Ranked list with error frequency
- **Use case**: Prioritize fixes for most common errors

---

### Comparative & Trend Metrics

**1. Period-over-Period Comparison**
- **Metrics**: Compare this week vs last week vs same week last year
- **Visualization**: Multi-line chart with period selection
- **Breakdowns**: 
  - Daily uploads
  - Approval rate
  - Processing time

**2. Moving Averages**
- **Metrics**: 
  - 7-day moving average of daily uploads
  - 30-day moving average of approval rate
- **Visualization**: Line chart with trend line
- **Use case**: Smooth out noise, identify true trends

**3. Growth Rate Indicators**
- **Metrics**:
  - Week-over-week growth %
  - Month-over-month growth %
  - YoY comparison
- **Visualization**: Delta indicators with color (green ↑, red ↓)

---

## Implementation Roadmap

### Phase 1 (MVP)
- KPI cards: Total videos generated, Total uploaded
- Upload timeline line chart with date range selector
- Channel upload distribution bar chart
- Basic time range filters (Last 7/30/90 days, YTD, All-time)

### Phase 2
- Pipeline funnel chart
- Upload success rate by channel
- Processing time distribution
- Content category breakdown

### Phase 3
- Sentiment analysis distribution
- Media asset reuse metrics
- Provider usage tracking
- Video performance metrics (if API integration)

### Phase 4
- Advanced filtering and drill-downs
- Custom date ranges
- Export functionality (CSV/PDF)
- Anomaly detection alerts

---

## Database Queries (Reference)

### Get video generation count
```sql
SELECT COUNT(*) as total_generated 
FROM video_generations 
WHERE status = 'completed' 
AND created_at >= NOW() - INTERVAL '30 days';
```

### Get upload timeline
```sql
SELECT 
  DATE(uploaded_at) as upload_date,
  COUNT(*) as videos_uploaded,
  platform
FROM video_uploads 
WHERE upload_status = 'completed'
AND uploaded_at >= NOW() - INTERVAL '90 days'
GROUP BY DATE(uploaded_at), platform
ORDER BY upload_date;
```

### Pipeline funnel
```sql
SELECT
  'ingested' as stage,
  COUNT(DISTINCT id) as count
FROM news
WHERE created_at >= NOW() - INTERVAL '30 days'
UNION ALL
SELECT
  'summarized' as stage,
  COUNT(DISTINCT article_id) as count
FROM article_summaries
WHERE created_at >= NOW() - INTERVAL '30 days'
UNION ALL
SELECT
  'audio_generated' as stage,
  COUNT(DISTINCT article_id) as count
FROM audio_transcripts
WHERE created_at >= NOW() - INTERVAL '30 days'
UNION ALL
SELECT
  'video_generated' as stage,
  COUNT(DISTINCT article_id) as count
FROM video_generations
WHERE created_at >= NOW() - INTERVAL '30 days'
UNION ALL
SELECT
  'approved' as stage,
  COUNT(DISTINCT id) as count
FROM video_generations
WHERE review_status = 'approved'
AND created_at >= NOW() - INTERVAL '30 days'
UNION ALL
SELECT
  'uploaded' as stage,
  COUNT(DISTINCT video_generation_id) as count
FROM video_uploads
WHERE upload_status = 'completed'
AND created_at >= NOW() - INTERVAL '30 days';
```

### Channel performance
```sql
SELECT 
  c.name as channel_name,
  COUNT(*) as total_uploads,
  SUM(CASE WHEN u.upload_status = 'completed' THEN 1 ELSE 0 END) as successful_uploads,
  ROUND(100.0 * SUM(CASE WHEN u.upload_status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate,
  SUM(u.view_count) as total_views
FROM video_uploads u
LEFT JOIN channels c ON u.channel_id = c.id
WHERE u.created_at >= NOW() - INTERVAL '30 days'
GROUP BY c.name
ORDER BY total_uploads DESC;
```

---

## Library Recommendations

- **Visualization**: Plotly (interactive, Streamlit-friendly)
- **Data handling**: Pandas with caching via `st.cache_data`
- **Date selection**: Streamlit `st.date_input()` and `st.selectbox()`
- **Layout**: Streamlit columns for KPI cards
