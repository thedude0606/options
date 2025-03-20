"""
Configuration module for Schwab API authentication.
This module contains the configuration settings for the Schwab API client.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Schwab API credentials
SCHWAB_APP_KEY = os.getenv("SCHWAB_APP_KEY", "kQjNEtGHLhWUE0ZCdiaAkLDUfjBGT8G0")
SCHWAB_APP_SECRET = os.getenv("SCHWAB_APP_SECRET", "dYPIYuVJiIuHMc1Y")
SCHWAB_CALLBACK_URL = os.getenv("SCHWAB_CALLBACK_URL", "https://127.0.0.1:8080")

# Python executable path
PYTHON_EXECUTABLE = "python3.11"  # Schwabdev requires Python 3.11+
