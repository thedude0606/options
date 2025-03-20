#!/usr/bin/env python3.11
"""
Authentication script for Schwab API.
This script handles the authentication process with Schwab API.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.auth.client import SchwabAuthClient
from src.auth.config import SCHWAB_APP_KEY, SCHWAB_APP_SECRET, SCHWAB_CALLBACK_URL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main function to authenticate with Schwab API.
    """
    # Load environment variables
    load_dotenv()
    
    logger.info("Starting Schwab API authentication process")
    
    # Initialize Schwab authentication client
    auth_client = SchwabAuthClient(
        app_key=SCHWAB_APP_KEY,
        app_secret=SCHWAB_APP_SECRET,
        callback_url=SCHWAB_CALLBACK_URL,
        tokens_file=os.path.join(os.path.dirname(__file__), '../../.env'),
        capture_callback=True
    )
    
    try:
        # Get Schwab client
        client = auth_client.get_client()
        logger.info("Schwab client initialized successfully")
        
        # Check if authenticated
        if auth_client.check_authentication():
            logger.info("Successfully authenticated with Schwab API")
            
            # Get account information
            accounts = client.account_linked()
            logger.info(f"Found {len(accounts)} linked accounts")
            
            # Print account information
            for account in accounts:
                logger.info(f"Account Number: {account.get('accountNumber', 'N/A')}")
                
            return True
        else:
            logger.error("Failed to authenticate with Schwab API")
            return False
    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
