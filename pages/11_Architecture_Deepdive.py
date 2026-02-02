"""
Detailed Architecture Documentation - Autodrop System Design
"""

import re

import streamlit as st
from streamlit_mermaid import st_mermaid

st.set_page_config(
    page_title="Detailed Architecture",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Detailed Architecture Documentation")

st.markdown("""
This page contains the comprehensive system architecture documentation for the Autodrop platform.
""")

st.markdown("---")

# Read and display the detailed architecture documentation
try:
    with open("docs/TECHNICAL_ARCHITECTURE.md", "r") as f:
        content = f.read()
    
    # Split content by mermaid code blocks while preserving order
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    
    # Split the content into parts: text and diagrams alternating
    parts = re.split(mermaid_pattern, content, flags=re.DOTALL)
    
    # Process parts: text at even indices, diagrams at odd indices
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Regular markdown content
            if part.strip():
                st.markdown(part)
        else:
            # Mermaid diagram - add dark theme config
            st.markdown("---")
            try:
                # Add dark theme configuration to diagram
                diagram_with_theme = f"%%{{init: {{'theme':'dark', 'themeVariables': {{'primaryColor':'#1f77b4', 'primaryBorderColor':'#7f7f7f', 'lineColor':'#7f7f7f', 'textColor':'#ffffff'}}}}}}%%\n{part}"
                st_mermaid(diagram_with_theme)
            except Exception as e:
                st.warning(f"Could not render diagram. Error: {e}")
                st.code(part, language="mermaid")
            st.markdown("---")
except FileNotFoundError:
    st.warning("Technical Architecture document not found. Please ensure the documentation file exists in the docs folder.")
except Exception as e:
    st.error(f"Error loading documentation: {e}")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("← Back to Quick Reference", width='stretch'):
        st.switch_page("pages/10_Architecture_Overview.py")

with col2:
    if st.button("Back to Home →", width='stretch'):
        st.switch_page("AutoDrop-App.py")
