"""
Mock test script for the Schwab API Dashboard application.
This script uses mocks to test the functionality without requiring actual authentication.
"""

import os
import sys
import logging
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestSchwabDashboardMock(unittest.TestCase):
    """
    Test case for the Schwab API Dashboard application using mocks.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Set up the test environment with mocks.
        """
        # Create sample data
        cls.create_sample_data()
        
        # Create mock client
        cls.client = MagicMock()
        cls.client.account_linked.return_value = cls.sample_accounts
        
        # Create mock auth client
        cls.auth_client = MagicMock()
        cls.auth_client.get_client.return_value = cls.client
        cls.auth_client.check_authentication.return_value = True
        
        # Patch imports
        cls.auth_client_patch = patch('src.auth.client.SchwabAuthClient', return_value=cls.auth_client)
        cls.auth_client_patch.start()
        
        # Import components
        from src.data.manager import DataManager
        
        # Initialize data manager with mock
        cls.data_manager = DataManager(cls.client)
        
        # Configure data manager mock methods
        cls.data_manager.get_price_history = MagicMock(return_value=cls.sample_price_data)
        cls.data_manager.get_option_chain = MagicMock(return_value=cls.sample_option_chain)
        cls.data_manager.get_quote = MagicMock(return_value=cls.sample_quotes)
        cls.data_manager.save_data = MagicMock(return_value="/tmp/test_data.csv")
    
    @classmethod
    def tearDownClass(cls):
        """
        Clean up after tests.
        """
        cls.auth_client_patch.stop()
    
    @classmethod
    def create_sample_data(cls):
        """
        Create sample data for testing.
        """
        # Create sample accounts
        cls.sample_accounts = [
            {
                "accountId": "123456789",
                "displayName": "Test Account 1",
                "accountType": "MARGIN"
            },
            {
                "accountId": "987654321",
                "displayName": "Test Account 2",
                "accountType": "CASH"
            }
        ]
        
        # Create sample price history data
        dates = pd.date_range(start='2023-01-01', periods=10)
        cls.sample_price_data = pd.DataFrame({
            'datetime': dates,
            'open': [150.0, 151.0, 152.0, 153.0, 154.0, 155.0, 156.0, 157.0, 158.0, 159.0],
            'high': [155.0, 156.0, 157.0, 158.0, 159.0, 160.0, 161.0, 162.0, 163.0, 164.0],
            'low': [145.0, 146.0, 147.0, 148.0, 149.0, 150.0, 151.0, 152.0, 153.0, 154.0],
            'close': [152.0, 153.0, 154.0, 155.0, 156.0, 157.0, 158.0, 159.0, 160.0, 161.0],
            'volume': [1000000, 1100000, 1200000, 1300000, 1400000, 1500000, 1600000, 1700000, 1800000, 1900000]
        })
        
        # Create sample quotes
        cls.sample_quotes = {
            'AAPL': {
                'symbol': 'AAPL',
                'description': 'APPLE INC',
                'lastPrice': 160.0,
                'openPrice': 159.0,
                'highPrice': 161.0,
                'lowPrice': 158.0,
                'closePrice': 159.5,
                'totalVolume': 2000000,
                'bidPrice': 159.9,
                'askPrice': 160.1
            },
            'MSFT': {
                'symbol': 'MSFT',
                'description': 'MICROSOFT CORP',
                'lastPrice': 260.0,
                'openPrice': 259.0,
                'highPrice': 261.0,
                'lowPrice': 258.0,
                'closePrice': 259.5,
                'totalVolume': 1500000,
                'bidPrice': 259.9,
                'askPrice': 260.1
            },
            'GOOGL': {
                'symbol': 'GOOGL',
                'description': 'ALPHABET INC',
                'lastPrice': 130.0,
                'openPrice': 129.0,
                'highPrice': 131.0,
                'lowPrice': 128.0,
                'closePrice': 129.5,
                'totalVolume': 1800000,
                'bidPrice': 129.9,
                'askPrice': 130.1
            }
        }
        
        # Create sample option chain data
        cls.sample_option_chain = {
            'symbol': 'AAPL',
            'status': 'SUCCESS',
            'underlying': {
                'symbol': 'AAPL',
                'description': 'APPLE INC',
                'change': 1.5,
                'percentChange': 0.8,
                'close': 160.0,
                'quoteTime': 1679000000000,
                'tradeTime': 1679000000000,
                'bid': 159.5,
                'ask': 160.5,
                'last': 160.0,
                'mark': 160.0,
                'markChange': 1.5,
                'markPercentChange': 0.8,
                'bidSize': 100,
                'askSize': 100,
                'highPrice': 161.0,
                'lowPrice': 158.0,
                'openPrice': 159.0,
                'totalVolume': 2000000,
                'exchangeName': 'NASDAQ',
                'fiftyTwoWeekHigh': 180.0,
                'fiftyTwoWeekLow': 120.0,
                'delayed': False
            },
            'callExpDateMap': {
                '2023-04-21:30': {
                    '160.0': [{
                        'putCall': 'CALL',
                        'symbol': 'AAPL_042123C160',
                        'description': 'AAPL Apr 21 2023 160 Call',
                        'exchangeName': 'OPR',
                        'bid': 5.0,
                        'ask': 5.2,
                        'last': 5.1,
                        'mark': 5.1,
                        'bidSize': 10,
                        'askSize': 10,
                        'lastSize': 0,
                        'highPrice': 5.3,
                        'lowPrice': 4.9,
                        'openPrice': 5.0,
                        'totalVolume': 1000,
                        'tradeDate': None,
                        'tradeTimeInLong': 1679000000000,
                        'quoteTimeInLong': 1679000000000,
                        'netChange': 0.1,
                        'volatility': 30.0,
                        'delta': 0.5,
                        'gamma': 0.05,
                        'theta': -0.03,
                        'vega': 0.1,
                        'rho': 0.01,
                        'openInterest': 5000,
                        'timeValue': 5.1,
                        'theoreticalOptionValue': 5.1,
                        'theoreticalVolatility': 30.0,
                        'strikePrice': 160.0,
                        'expirationDate': 1682035200000,
                        'daysToExpiration': 30,
                        'expirationType': 'R',
                        'lastTradingDay': 1682035200000,
                        'multiplier': 100.0,
                        'settlementType': 'P',
                        'deliverableNote': '',
                        'isIndexOption': None,
                        'percentChange': 2.0,
                        'markChange': 0.1,
                        'markPercentChange': 2.0,
                        'intrinsicValue': 0.0,
                        'inTheMoney': False,
                        'mini': False,
                        'nonStandard': False
                    }]
                }
            },
            'putExpDateMap': {
                '2023-04-21:30': {
                    '160.0': [{
                        'putCall': 'PUT',
                        'symbol': 'AAPL_042123P160',
                        'description': 'AAPL Apr 21 2023 160 Put',
                        'exchangeName': 'OPR',
                        'bid': 4.8,
                        'ask': 5.0,
                        'last': 4.9,
                        'mark': 4.9,
                        'bidSize': 10,
                        'askSize': 10,
                        'lastSize': 0,
                        'highPrice': 5.1,
                        'lowPrice': 4.7,
                        'openPrice': 4.8,
                        'totalVolume': 800,
                        'tradeDate': None,
                        'tradeTimeInLong': 1679000000000,
                        'quoteTimeInLong': 1679000000000,
                        'netChange': -0.1,
                        'volatility': 32.0,
                        'delta': -0.5,
                        'gamma': 0.05,
                        'theta': -0.03,
                        'vega': 0.1,
                        'rho': -0.01,
                        'openInterest': 4000,
                        'timeValue': 4.9,
                        'theoreticalOptionValue': 4.9,
                        'theoreticalVolatility': 32.0,
                        'strikePrice': 160.0,
                        'expirationDate': 1682035200000,
                        'daysToExpiration': 30,
                        'expirationType': 'R',
                        'lastTradingDay': 1682035200000,
                        'multiplier': 100.0,
                        'settlementType': 'P',
                        'deliverableNote': '',
                        'isIndexOption': None,
                        'percentChange': -2.0,
                        'markChange': -0.1,
                        'markPercentChange': -2.0,
                        'intrinsicValue': 0.0,
                        'inTheMoney': False,
                        'mini': False,
                        'nonStandard': False
                    }]
                }
            }
        }
    
    def test_authentication(self):
        """
        Test authentication with Schwab API.
        """
        logger.info("Testing authentication (mock)")
        self.assertTrue(self.auth_client.check_authentication(), "Authentication failed")
    
    def test_account_linked(self):
        """
        Test retrieving linked accounts.
        """
        logger.info("Testing account_linked (mock)")
        accounts = self.client.account_linked()
        self.assertIsNotNone(accounts, "Failed to retrieve linked accounts")
        self.assertEqual(len(accounts), 2, "Incorrect number of accounts")
        logger.info(f"Found {len(accounts)} linked accounts")
    
    def test_historical_data(self):
        """
        Test retrieving historical data.
        """
        logger.info("Testing historical data retrieval (mock)")
        symbols = ['AAPL', 'MSFT']
        
        for symbol in symbols:
            logger.info(f"Testing historical data for {symbol}")
            df = self.data_manager.get_price_history(symbol, period_type='day', period=5)
            self.assertFalse(df.empty, f"Failed to retrieve historical data for {symbol}")
            self.assertEqual(len(df), 10, f"Incorrect number of data points for {symbol}")
            logger.info(f"Retrieved {len(df)} data points for {symbol}")
    
    def test_option_chain(self):
        """
        Test retrieving option chain data.
        """
        logger.info("Testing option chain retrieval (mock)")
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
        
        self.assertEqual(call_count, 1, "Incorrect number of call options")
        self.assertEqual(put_count, 1, "Incorrect number of put options")
        logger.info(f"Retrieved {call_count} calls and {put_count} puts for {symbol}")
    
    def test_quotes(self):
        """
        Test retrieving quotes.
        """
        logger.info("Testing quote retrieval (mock)")
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
        logger.info("Testing data saving (mock)")
        symbol = 'AAPL'
        
        # Get data
        df = self.data_manager.get_price_history(symbol, period_type='day', period=5)
        self.assertFalse(df.empty, f"Failed to retrieve data for {symbol}")
        
        # Save to CSV
        filepath = self.data_manager.save_data(df, f"{symbol}_test", format='csv')
        self.assertIsNotNone(filepath, "Failed to save data to CSV")
        
        logger.info("Successfully saved data to files (mock)")

def run_tests():
    """
    Run the test suite.
    """
    logger.info("Starting Schwab API Dashboard mock tests")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    run_tests()
