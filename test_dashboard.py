"""
Dashboard test script for the Schwab API Dashboard application.
This script tests the functionality of the dashboard components.
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

class TestDashboard(unittest.TestCase):
    """
    Test case for the dashboard components.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Set up the test environment.
        """
        # Mock data manager
        cls.data_manager = MagicMock()
        
        # Import dashboard components
        from src.dashboard.dashboard import Dashboard
        from src.dashboard.utils import create_candlestick_chart, format_option_chain_table
        from src.dashboard.realtime_integration import RealTimeIntegration
        from src.dashboard.realtime_handler import RealTimeHandler
        
        # Store imported components
        cls.Dashboard = Dashboard
        cls.create_candlestick_chart = create_candlestick_chart
        cls.format_option_chain_table = format_option_chain_table
        cls.RealTimeIntegration = RealTimeIntegration
        cls.RealTimeHandler = RealTimeHandler
        
        # Create sample data
        cls.create_sample_data()
    
    @classmethod
    def create_sample_data(cls):
        """
        Create sample data for testing.
        """
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
    
    def test_dashboard_initialization(self):
        """
        Test dashboard initialization.
        """
        logger.info("Testing dashboard initialization")
        
        # Configure mock data manager
        self.data_manager.get_price_history.return_value = self.sample_price_data
        self.data_manager.get_option_chain.return_value = self.sample_option_chain
        
        # Initialize dashboard
        dashboard = self.Dashboard(self.data_manager)
        
        # Verify dashboard attributes
        self.assertIsNotNone(dashboard.app, "Dashboard app not initialized")
        self.assertIsNotNone(dashboard.server, "Dashboard server not initialized")
        self.assertIsNotNone(dashboard.realtime, "Real-time integration not initialized")
        self.assertIsNotNone(dashboard.realtime_handler, "Real-time handler not initialized")
        
        logger.info("Dashboard initialization successful")
    
    def test_candlestick_chart_creation(self):
        """
        Test candlestick chart creation.
        """
        logger.info("Testing candlestick chart creation")
        
        # Create chart
        figure = self.create_candlestick_chart(self.sample_price_data, "Test Chart")
        
        # Verify figure
        self.assertIsNotNone(figure, "Failed to create candlestick chart")
        self.assertIn("data", figure, "Chart data missing")
        self.assertIn("layout", figure, "Chart layout missing")
        self.assertEqual(figure["layout"]["title"], "Test Chart", "Chart title incorrect")
        
        logger.info("Candlestick chart creation successful")
    
    def test_option_chain_table_formatting(self):
        """
        Test option chain table formatting.
        """
        logger.info("Testing option chain table formatting")
        
        # Format table for calls
        calls_table = self.format_option_chain_table(self.sample_option_chain, "calls")
        
        # Format table for puts
        puts_table = self.format_option_chain_table(self.sample_option_chain, "puts")
        
        # Format table for both
        both_table = self.format_option_chain_table(self.sample_option_chain, "both")
        
        # Verify tables
        self.assertIsNotNone(calls_table, "Failed to format calls table")
        self.assertIsNotNone(puts_table, "Failed to format puts table")
        self.assertIsNotNone(both_table, "Failed to format both table")
        
        logger.info("Option chain table formatting successful")
    
    def test_realtime_integration(self):
        """
        Test real-time integration.
        """
        logger.info("Testing real-time integration")
        
        # Initialize real-time integration
        realtime = self.RealTimeIntegration(self.data_manager)
        
        # Register callback
        def test_callback(message):
            pass
        
        success = realtime.register_callback("QUOTE", test_callback)
        self.assertTrue(success, "Failed to register callback")
        
        # Verify callback registration
        self.assertIn("QUOTE", realtime.data_callbacks, "Callback not registered")
        self.assertEqual(len(realtime.data_callbacks["QUOTE"]), 1, "Incorrect number of callbacks")
        
        logger.info("Real-time integration testing successful")
    
    def test_realtime_handler(self):
        """
        Test real-time handler.
        """
        logger.info("Testing real-time handler")
        
        # Mock dashboard
        dashboard = MagicMock()
        dashboard.data_manager = self.data_manager
        dashboard.realtime = self.RealTimeIntegration(self.data_manager)
        
        # Initialize real-time handler
        handler = self.RealTimeHandler(dashboard)
        
        # Test quote update
        quote_message = {
            'symbol': 'AAPL',
            'openPrice': 150.0,
            'highPrice': 155.0,
            'lowPrice': 145.0,
            'lastPrice': 152.0,
            'totalVolume': 1000000
        }
        
        handler.handle_quote_update(quote_message)
        
        # Verify data update
        self.assertIn('AAPL', handler.price_data, "Price data not updated")
        self.assertEqual(len(handler.price_data['AAPL']), 1, "Incorrect number of price data points")
        
        # Test option update
        option_message = {
            'symbol': 'AAPL_042123C160',
            'underlying': 'AAPL',
            'strikePrice': 160.0,
            'expirationDate': '2023-04-21',
            'putCall': 'CALL',
            'bidPrice': 5.0,
            'askPrice': 5.2,
            'lastPrice': 5.1,
            'totalVolume': 1000,
            'openInterest': 5000,
            'delta': 0.5,
            'gamma': 0.05,
            'theta': -0.03,
            'vega': 0.1
        }
        
        handler.handle_option_update(option_message)
        
        # Verify data update
        self.assertIn('AAPL', handler.option_data, "Option data not updated")
        self.assertIn('AAPL_042123C160', handler.option_data['AAPL'], "Option symbol not found")
        
        logger.info("Real-time handler testing successful")

def run_dashboard_tests():
    """
    Run the dashboard test suite.
    """
    logger.info("Starting dashboard tests")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    run_dashboard_tests()
