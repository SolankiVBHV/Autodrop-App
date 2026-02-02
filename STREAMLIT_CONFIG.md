# Streamlit Configuration Guide

This app supports both **local development** and **cloud deployment** using Streamlit's secrets system.

## Local Development

### Option 1: Using `.env` file (Existing Setup)
Keep your `.env` file as is. The app will automatically fall back to it:

```bash
# .env
CLOUD_HOST=IP
CLOUD_DB_PORT=5432
CLOUD_READONLY_USER=your_user
CLOUD_READONLY_DB_PASSWORD=your_password
US_SPORTS_CENTRAL_CHANNEL=https://www.youtube.com/...
```

Run the app normally:
```bash
streamlit run Summary.py
```

### Option 2: Using `.streamlit/secrets.toml` (Recommended for all environments)
Secrets are automatically loaded by Streamlit and override `.env` values.

The file is already created at `.streamlit/secrets.toml` with your configuration.

## Cloud Deployment (Streamlit Cloud / Docker)

When deploying to Streamlit Cloud:

1. **Never commit `.streamlit/secrets.toml`** to public repos (it contains credentials)
2. In Streamlit Cloud dashboard, add secrets in **Settings → Secrets**:

```toml
CLOUD_HOST = "your_host"
CLOUD_DB_PORT = 5432
CLOUD_READONLY_USER = "your_user"
CLOUD_READONLY_DB_PASSWORD = "your_password"

[channels]
US_SPORTS_CENTRAL = "https://www.youtube.com/..."
US_NOW_LIVE = "https://www.youtube.com/..."
```

## File Structure

```
.streamlit/
├── config.toml      # App configuration (theme, UI settings) - Safe to commit
└── secrets.toml     # Credentials (NEVER commit to public repos)

.env                 # Local development credentials (Git ignored)
```

## How It Works

The `config_loader.py` module automatically:
1. **Checks `st.secrets` first** (Streamlit Cloud / Docker)
2. **Falls back to `.env`** (Local development)
3. **Falls back to OS environment variables**

This means the same code works everywhere with zero changes!

### Usage in Code

```python
from config_loader import get_db_config, get_channel_links, get_config_value

# Get database config
db_config = get_db_config()

# Get channel links
channels = get_channel_links()

# Get individual config values
host = get_config_value("CLOUD_HOST", default="localhost")
```

## Docker Deployment

Add secrets to your Docker environment:

```dockerfile
ENV CLOUD_HOST=your_host
ENV CLOUD_READONLY_USER=your_user
ENV CLOUD_READONLY_DB_PASSWORD=your_password
```

Or use a `.env.docker` file and mount it.

## .gitignore

Make sure your `.gitignore` includes:
```
.env
.streamlit/secrets.toml
.streamlit/secrets.*.toml
```

This prevents accidental credential leaks!
