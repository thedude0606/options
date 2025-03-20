"""
Main application entry point.
This module initializes the Schwab API client and dashboard.
"""

import os
from dotenv import load_dotenv
from src.auth.client import SchwabAuthClient

# Load environment variables
load_dotenv()

def main():
    """
    Main application entry point.
    Initializes the Schwab API client and dashboard.
    """
    # Get credentials from environment variables or use defaults
    app_key = os.getenv("SCHWAB_APP_KEY", "kQjNEtGHLhWUE0ZCdiaAkLDUfjBGT8G0")
    app_secret = os.getenv("SCHWAB_APP_SECRET", "dYPIYuVJiIuHMc1Y")
    callback_url = os.getenv("SCHWAB_CALLBACK_URL", "https://127.0.0.1:8080")
    
    # Initialize Schwab client
    auth_client = SchwabAuthClient(
        app_key=app_key,
        app_secret=app_secret,
        callback_url=callback_url
    )
    
    client = auth_client.get_client()
    print("Schwab client initialized successfully.")
    
    # TODO: Initialize dashboard and data components
    
if __name__ == "__main__":
    main()
