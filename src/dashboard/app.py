"""
Main dashboard application entry point.
This module initializes the dashboard and connects it to the data manager.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main function to initialize and run the dashboard.
    """
    # Load environment variables
    load_dotenv()
    
    # Check Python version
    if sys.version_info < (3, 11):
        logger.error("Python 3.11 or higher is required for this application")
        logger.info("Current Python version: %s.%s.%s", sys.version_info.major, 
                   sys.version_info.minor, sys.version_info.micro)
        logger.info("Please run this application with Python 3.11 or higher")
        return False
    
    try:
        # Import here to ensure Python 3.11 compatibility
        from src.auth.client import SchwabAuthClient
        from src.data.manager import DataManager
        from src.dashboard.dashboard import Dashboard
        
        # Initialize Schwab client
        logger.info("Initializing Schwab authentication client")
        auth_client = SchwabAuthClient()
        client = auth_client.get_client()
        
        # Check authentication
        if not auth_client.check_authentication():
            logger.error("Failed to authenticate with Schwab API")
            return False
        
        logger.info("Successfully authenticated with Schwab API")
        
        # Initialize data manager
        logger.info("Initializing data manager")
        data_manager = DataManager(client)
        
        # Initialize dashboard
        logger.info("Initializing dashboard")
        dashboard = Dashboard(data_manager)
        
        # Run dashboard
        logger.info("Starting dashboard server on port 8050")
        dashboard.run(debug=True, port=8050)
        
        return True
    except Exception as e:
        logger.error(f"Error in dashboard application: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
