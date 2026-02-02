"""
Videos Page - Top Shorts from Channels
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

import streamlit as st
import yt_dlp
from dotenv import dotenv_values

st.set_page_config(
    page_title="Videos",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for portrait video display
st.markdown("""
<style>
    iframe {
        aspect-ratio: 9/16 !important;
        max-width: 300px !important;
        width: 100% !important;
        height: auto !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎬 Channel Shorts")

st.markdown("---")


def _load_channel_links() -> Dict[str, str]:
    env_file_values = dotenv_values(".env")
    env_runtime = {k: v for k, v in os.environ.items() if k.endswith("_CHANNEL")}

    merged = {**env_file_values, **env_runtime}
    channels = {}
    for key, value in merged.items():
        if key and key.endswith("_CHANNEL") and value:
            name = key.replace("_CHANNEL", "").replace("_", " ").title()
            channels[name] = value.strip()
    return dict(sorted(channels.items(), key=lambda x: x[0]))


@st.cache_data(ttl=3600)
def _fetch_shorts(channel_url: str, max_entries: int = 20) -> List[Dict[str, str]]:
    shorts_url = channel_url.rstrip("/") + "/shorts"

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "nocheckcertificate": True,
    }

    videos: List[Dict[str, str]] = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(shorts_url, download=False)
        entries = [e for e in info.get("entries", []) if e]

        for entry in entries[:max_entries]:
            video_id = entry.get("id")
            if video_id:
                videos.append(
                    {
                        "id": video_id,
                        "title": entry.get("title") or "Untitled",
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "thumbnail": entry.get("thumbnail") or "",
                    }
                )

    return videos


channels = _load_channel_links()

if not channels:
    st.warning("No *_CHANNEL entries found in .env or environment variables.")
    st.stop()

max_videos = st.slider("Videos per channel", min_value=3, max_value=12, value=3, step=1)

# Fetch all channels in parallel and display as they complete
progress_placeholder = st.empty()
completed = 0
total_channels = len(channels)

def fetch_channel_videos(name, url):
    try:
        videos = _fetch_shorts(url, max_entries=max_videos)
        return name, url, videos, None
    except Exception as e:
        return name, url, [], str(e)

with ThreadPoolExecutor(max_workers=len(channels)) as executor:
    futures = {
        executor.submit(fetch_channel_videos, name, url): name 
        for name, url in channels.items()
    }
    
    for future in as_completed(futures):
        name, url, videos, error = future.result()
        completed += 1
        
        progress_placeholder.info(f"Loading... {completed}/{total_channels} channels loaded")
        
        st.markdown(f"### [{name}]({url})")

        if error:
            st.warning(f"Could not load videos for {name}: {error}")
            st.markdown("---")
            continue

        if not videos:
            st.info("No Shorts found for this channel.")
            st.markdown("---")
            continue

        # Use fewer columns for portrait videos (2 or 3 instead of 4)
        num_cols = min(len(videos), 3)
        cols = st.columns(num_cols)
        for idx, video in enumerate(videos):
            col = cols[idx % num_cols]
            with col:
                st.video(video["url"])
                st.markdown(f"**{video['title']}**")

        st.markdown("---")

progress_placeholder.empty()
