"""
Test script for the Schwab API Dashboard application.
This script tests the functionality of the authentication, data retrieval, and dashboard components.
"""

import os
import sys
import logging
import unittest
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestSchwabDashboard(unittest.TestCase):
    """
    Test case for the Schwab API Dashboard application.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Set up the test environment.
        """
        # Load environment variables
        load_dotenv()
        
        # Check Python version
        if sys.version_info < (3, 11):
            logger.error("Python 3.11 or higher is required for this application")
            logger.info("Current Python version: %s.%s.%s", sys.version_info.major, 
                       sys.version_info.minor, sys.version_info.micro)
            sys.exit(1)
        
        # Import components
        from src.auth.client import SchwabAuthClient
        from src.data.manager import DataManager
        
        # Initialize Schwab client
        logger.info("Initializing Schwab authentication client for testing")
        cls.auth_client = SchwabAuthClient()
        cls.client = cls.auth_client.get_client()
        
        # Initialize data manager
        logger.info("Initializing data manager for testing")
        cls.data_manager = DataManager(cls.client)
    
    def test_authentication(self):
        """
        Test authentication with Schwab API.
        """
        logger.info("Testing authentication")
        self.assertTrue(self.auth_client.check_authentication(), "Authentication failed")
    
    def test_account_linked(self):
        """
        Test retrieving linked accounts.
        """
        logger.info("Testing account_linked")
        accounts = self.client.account_linked()
        self.assertIsNotNone(accounts, "Failed to retrieve linked accounts")
        logger.info(f"Found {len(accounts)} linked accounts")
    
    def test_historical_data(self):
        """
        Test retrieving historical data.
        """
        logger.info("Testing historical data retrieval")
        symbols = ['AAPL', 'MSFT']
        
        for symbol in symbols:
            logger.info(f"Testing historical data for {symbol}")
            df = self.data_manager.get_price_history(symbol, period_type='day', period=5)
            self.assertFalse(df.empty, f"Failed to retrieve historical data for {symbol}")
            logger.info(f"Retrieved {len(df)} data points for {symbol}")
    
    def test_option_chain(self):
        """
        Test retrieving option chain data.
        """
        logger.info("Testing option chain retrieval")
        symbol = 'AAPL'
        
        option_chain = self.data_manager.get_option_chain(symbol)
        self.assertIsNotNone(option_chain, f"Failed to retrieve option chain for {symbol}")
        self.assertIn('callExpDateMap', option_chain, "Option chain missing call data")
        self.assertIn('putExpDateMap', option_chain, "Option chain missing put data")
        
        # Count total options
        call_count = 0
        for exp_date, strikes in option_chain['callExpDateMap'].items():
            for strike, options in strikes.items():
                call_count += len(options)
        
        put_count = 0
        for exp_date, strikes in option_chain['putExpDateMap'].items():
            for strike, options in strikes.items():
                put_count += len(options)
        
        logger.info(f"Retrieved {call_count} calls and {put_count} puts for {symbol}")
    
    def test_quotes(self):
        """
        Test retrieving quotes.
        """
        logger.info("Testing quote retrieval")
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        
        quotes = self.data_manager.get_quote(symbols)
        self.assertIsNotNone(quotes, "Failed to retrieve quotes")
        
        for symbol in symbols:
            self.assertIn(symbol, quotes, f"Quote for {symbol} not found")
        
        logger.info(f"Successfully retrieved quotes for {', '.join(symbols)}")
    
    def test_data_saving(self):
        """
        Test saving data to file.
        """
        logger.info("Testing data saving")
        symbol = 'AAPL'
        
        # Get data
        df = self.data_manager.get_price_history(symbol, period_type='day', period=5)
        self.assertFalse(df.empty, f"Failed to retrieve data for {symbol}")
        
        # Save to CSV
        filepath = self.data_manager.save_data(df, f"{symbol}_test", format='csv')
        self.assertIsNotNone(filepath, "Failed to save data to CSV")
        self.assertTrue(os.path.exists(filepath), f"CSV file {filepath} does not exist")
        
        # Save to JSON
        filepath = self.data_manager.save_data(df, f"{symbol}_test", format='json')
        self.assertIsNotNone(filepath, "Failed to save data to JSON")
        self.assertTrue(os.path.exists(filepath), f"JSON file {filepath} does not exist")
        
        logger.info("Successfully saved data to files")

def run_tests():
    """
    Run the test suite.
    """
    logger.info("Starting Schwab API Dashboard tests")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    run_tests()
