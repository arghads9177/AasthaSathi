"""
Configuration for AasthaSathi UI

Manages API endpoints, credentials, and application settings.
"""

import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# API Configuration
AASTHASATHI_API_URL = os.getenv("AASTHASATHI_API_URL", "http://localhost:8000")
AASTHASATHI_API_USERNAME = os.getenv("API_USERNAME", "aastha_admin")
AASTHASATHI_API_PASSWORD = os.getenv("API_PASSWORD", "aastha_secure_2025")

# MyAastha Login API
MYAASTHA_LOGIN_URL = "https://web.myaastha.in/cobankapi/api/user/signin"
MYAASTHA_AUTH_TOKEN = os.getenv("BANKING_AUTH_KEY", "Bearer QUFzdDhAOmNCMW5L")

# UI Settings
APP_TITLE = "AasthaSathi - AI Banking Assistant"
APP_ICON = "🏦"
PAGE_LAYOUT = "wide"

# Theme Colors (Aastha Brand)
THEME_PRIMARY_COLOR = "#0891B2"  # Cyan
THEME_BACKGROUND_COLOR = "#F8FAFC"  # Light Gray
THEME_SECONDARY_BG_COLOR = "#FFFFFF"  # White
THEME_TEXT_COLOR = "#1F2937"  # Dark Gray

# Session Settings
SESSION_TIMEOUT_MINUTES = 30
MAX_CHAT_HISTORY = 50

# API Request Settings
REQUEST_TIMEOUT = 60  # seconds
MAX_RETRIES = 3
