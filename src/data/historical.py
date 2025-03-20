"""
Data retrieval module for historical stock data.
This module handles fetching historical stock data from the Schwab API.
"""

import logging
import pandas as pd
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HistoricalStockData:
    """
    Class for retrieving historical stock data from Schwab API.
    """
    
    def __init__(self, client):
        """
        Initialize the historical stock data retriever.
        
        Args:
            client (schwabdev.Client): Initialized Schwab client
        """
        self.client = client
        
    def get_price_history(self, symbol, period_type='day', period=10, 
                         frequency_type='minute', frequency=1):
        """
        Get historical price data for a symbol.
        
        Args:
            symbol (str): Stock symbol
            period_type (str): Type of period ('day', 'month', 'year', 'ytd')
            period (int): Number of periods
            frequency_type (str): Type of frequency ('minute', 'daily', 'weekly', 'monthly')
            frequency (int): Frequency
            
        Returns:
            pandas.DataFrame: Historical price data
        """
        try:
            logger.info(f"Retrieving price history for {symbol}")
            
            # Call Schwab API to get price history
            response = self.client.price_history(
                symbol=symbol,
                period_type=period_type,
                period=period,
                frequency_type=frequency_type,
                frequency=frequency
            )
            
            if not response or 'candles' not in response:
                logger.error(f"Failed to retrieve price history for {symbol}")
                return pd.DataFrame()
            
            # Convert response to DataFrame
            candles = response['candles']
            if not candles:
                logger.warning(f"No price data found for {symbol}")
                return pd.DataFrame()
            
            df = pd.DataFrame(candles)
            
            # Convert datetime
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            
            logger.info(f"Successfully retrieved {len(df)} price points for {symbol}")
            return df
        
        except Exception as e:
            logger.error(f"Error retrieving price history for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_option_chain(self, symbol, strike_count=10, include_quotes=True,
                        strategy='SINGLE', interval=None, strike=None,
                        range='ALL', from_date=None, to_date=None,
                        exp_month='ALL', option_type='ALL'):
        """
        Get option chain data for a symbol.
        
        Args:
            symbol (str): Stock symbol
            strike_count (int): Number of strikes to return
            include_quotes (bool): Include quotes
            strategy (str): Option strategy
            interval (float): Strike interval
            strike (float): Strike price
            range (str): Range ('ITM', 'NTM', 'OTM', 'SAK', 'SBK', 'SNK', 'ALL')
            from_date (str): From date (YYYY-MM-DD)
            to_date (str): To date (YYYY-MM-DD)
            exp_month (str): Expiration month ('JAN', 'FEB', etc., or 'ALL')
            option_type (str): Option type ('CALL', 'PUT', 'ALL')
            
        Returns:
            dict: Option chain data
        """
        try:
            logger.info(f"Retrieving option chain for {symbol}")
            
            # Call Schwab API to get option chain
            response = self.client.option_chain(
                symbol=symbol,
                strike_count=strike_count,
                include_quotes=include_quotes,
                strategy=strategy,
                interval=interval,
                strike=strike,
                range=range,
                from_date=from_date,
                to_date=to_date,
                exp_month=exp_month,
                option_type=option_type
            )
            
            if not response:
                logger.error(f"Failed to retrieve option chain for {symbol}")
                return {}
            
            logger.info(f"Successfully retrieved option chain for {symbol}")
            return response
        
        except Exception as e:
            logger.error(f"Error retrieving option chain for {symbol}: {str(e)}")
            return {}
    
    def get_quote(self, symbols):
        """
        Get quotes for one or more symbols.
        
        Args:
            symbols (str or list): Symbol or list of symbols
            
        Returns:
            dict: Quote data
        """
        try:
            if isinstance(symbols, str):
                symbols = [symbols]
                
            logger.info(f"Retrieving quotes for {', '.join(symbols)}")
            
            # Call Schwab API to get quotes
            response = self.client.quotes(symbols=symbols)
            
            if not response:
                logger.error(f"Failed to retrieve quotes for {', '.join(symbols)}")
                return {}
            
            logger.info(f"Successfully retrieved quotes for {', '.join(symbols)}")
            return response
        
        except Exception as e:
            logger.error(f"Error retrieving quotes for {', '.join(symbols)}: {str(e)}")
            return {}
    
    def save_to_csv(self, data, filename):
        """
        Save data to CSV file.
        
        Args:
            data (pandas.DataFrame): Data to save
            filename (str): Filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data.to_csv(filename, index=False)
            logger.info(f"Data saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving data to {filename}: {str(e)}")
            return False
