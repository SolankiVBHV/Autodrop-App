"""
Config loader - Support both Streamlit secrets and .env files
"""
import os
from typing import Any, Dict

import streamlit as st
from dotenv import dotenv_values


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get config value from Streamlit secrets first, then fall back to .env
    
    Args:
        key: Configuration key (e.g., "CLOUD_HOST")
        default: Default value if not found
        
    Returns:
        Configuration value
    """
    try:
        # Try Streamlit secrets first
        if key in st.secrets:
            return st.secrets[key]
    except (FileNotFoundError, KeyError, AttributeError):
        pass
    
    # Fall back to environment variables and .env
    if key in os.environ:
        return os.environ[key]
    
    env_values = dotenv_values(".env")
    if key in env_values:
        return env_values[key]
    
    return default


def get_channel_links() -> Dict[str, str]:
    """
    Get YouTube channel links from Streamlit secrets or .env
    
    Returns:
        Dictionary of channel names to URLs
    """
    channels = {}
    
    try:
        # Try Streamlit secrets first (TOML format with [channels] section)
        if "channels" in st.secrets:
            for name, url in st.secrets["channels"].items():
                channels[name] = url
            return channels
    except (FileNotFoundError, KeyError, AttributeError):
        pass
    
    # Fall back to .env format (KEY_CHANNEL=url)
    env_file_values = dotenv_values(".env")
    env_runtime = {k: v for k, v in os.environ.items() if k.endswith("_CHANNEL")}
    
    merged = {**env_file_values, **env_runtime}
    for key, value in merged.items():
        if key and key.endswith("_CHANNEL") and value:
            name = key.replace("_CHANNEL", "").replace("_", " ").title()
            channels[name] = value.strip()
    
    return dict(sorted(channels.items(), key=lambda x: x[0]))


def get_db_config() -> Dict[str, Any]:
    """
    Get database configuration from Streamlit secrets or .env
    
    Returns:
        Dictionary with database connection parameters
    """
    return {
        "host": get_config_value("CLOUD_HOST"),
        "port": int(get_config_value("CLOUD_DB_PORT", 5432)),
        "database": get_config_value("CLOUD_DATABASE_NAME", "autodrop"),
        "user": get_config_value("CLOUD_READONLY_USER"),
        "password": get_config_value("CLOUD_READONLY_DB_PASSWORD"),
    }
