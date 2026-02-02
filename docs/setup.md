# Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Autodrop-App.git
cd Autodrop-App
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### Local Development

```bash
streamlit run streamlit_app.py
```

The application will open in your default browser at `http://localhost:8501`.

### Development Server Options

```bash
# Run with debug enabled
streamlit run streamlit_app.py --logger.level=debug

# Run on specific port
streamlit run streamlit_app.py --server.port 8502

# Run in headless mode
streamlit run streamlit_app.py --headless
```

## Configuration

### Streamlit Config

Edit `.streamlit/config.toml` to customize:
- **Theme** - Colors and font settings
- **Server** - Port, upload limits, security settings
- **Logger** - Logging level

### Example Config

```toml
[theme]
primaryColor = "#FF6B35"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"

[server]
maxUploadSize = 200
port = 8501
```

## Troubleshooting

### Port Already in Use

If port 8501 is already in use:
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Dependencies Installation Issues

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Deployment

For production deployment, see your hosting platform's documentation (Streamlit Cloud, Heroku, AWS, etc.).
