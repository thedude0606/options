"""
Main application entry point.
This module initializes the Schwab API client and dashboard.
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
    Main application entry point.
    Initializes the Schwab API client and dashboard.
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
        from src.dashboard.app import main as run_dashboard
        
        # Enable debug logging
        logging.getLogger('src.data.realtime').setLevel(logging.DEBUG)
        logging.getLogger('src.dashboard.realtime_integration').setLevel(logging.DEBUG)
        logging.getLogger('src.dashboard.realtime_handler').setLevel(logging.DEBUG)
        
        # Initialize Schwab client
        auth_client = SchwabAuthClient()
        client = auth_client.get_client()
        
        logger.info("Schwab client initialized successfully")
        
        # Check authentication
        auth_status = auth_client.check_authentication()
        if not auth_status:
            logger.warning("Authentication check returned False, but continuing anyway for development purposes")
            # Uncomment the line below in production
            # return False
        
        # Initialize data manager
        data_manager = DataManager(client)
        
        # Get a quote for a test symbol
        test_symbol = 'AAPL'
        logger.info(f"Testing data retrieval with symbol: {test_symbol}")
        quote = data_manager.get_quote(test_symbol)
        logger.info(f"Quote data: {quote}")
        
        # Try to start streaming explicitly
        logger.info("Attempting to start real-time streaming manually")
        streaming_result = data_manager.start_streaming(
            symbols=['AAPL', 'MSFT'], 
            handlers={'QUOTE': lambda x: logger.info(f"QUOTE update: {x}")}
        )
        logger.info(f"Streaming start result: {streaming_result}")
        
        # Initialize and run dashboard
        logger.info("Starting dashboard application")
        run_dashboard()
        
        return True
    except Exception as e:
        logger.error(f"Error in main application: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
