"""
Data manager module for coordinating data retrieval operations.
This module provides a unified interface for accessing both historical and real-time data.
"""

import logging
import os
import pandas as pd
from datetime import datetime

from .historical import HistoricalStockData
from .streamer_singleton import StreamerSingleton

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataManager:
    """
    Class for managing data retrieval operations.
    Provides a unified interface for accessing both historical and real-time data.
    """
    
    def __init__(self, client):
        """
        Initialize the data manager.
        
        Args:
            client (schwabdev.Client): Initialized Schwab client
        """
        self.client = client
        self.historical_data = HistoricalStockData(client)
        # Use the singleton pattern for real-time data streamer
        self.realtime_data = StreamerSingleton.get_instance(client)
        self.data_cache = {}
        self.data_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
            logger.info(f"Created data directory: {self.data_directory}")
    
    def get_price_history(self, symbol, period_type='day', period=10, 
                         frequency_type='minute', frequency=1, use_cache=True):
        """
        Get historical price data for a symbol.
        
        Args:
            symbol (str): Stock symbol
            period_type (str): Type of period ('day', 'month', 'year', 'ytd')
            period (int): Number of periods
            frequency_type (str): Type of frequency ('minute', 'daily', 'weekly', 'monthly')
            frequency (int): Frequency
            use_cache (bool): Whether to use cached data if available
            
        Returns:
            pandas.DataFrame: Historical price data
        """
        # Generate cache key
        cache_key = f"{symbol}_{period_type}_{period}_{frequency_type}_{frequency}"
        
        # Check cache if enabled
        if use_cache and cache_key in self.data_cache:
            logger.info(f"Using cached price history for {symbol}")
            return self.data_cache[cache_key]
        
        # Get data from historical data retriever
        df = self.historical_data.get_price_history(
            symbol=symbol,
            period_type=period_type,
            period=period,
            frequency_type=frequency_type,
            frequency=frequency
        )
        
        # Cache the data if not empty
        if not df.empty:
            self.data_cache[cache_key] = df
        
        return df
        
    def get_historical_data(self, symbol, period_type='day', period=10, 
                           frequency_type='minute', frequency=1, use_cache=True):
        """
        Alias for get_price_history to maintain compatibility with dashboard.
        
        Args:
            symbol (str): Stock symbol
            period_type (str): Type of period ('day', 'month', 'year', 'ytd')
            period (int): Number of periods
            frequency_type (str): Type of frequency ('minute', 'daily', 'weekly', 'monthly')
            frequency (int): Frequency
            use_cache (bool): Whether to use cached data if available
            
        Returns:
            pandas.DataFrame: Historical price data
        """
        return self.get_price_history(
            symbol=symbol,
            period_type=period_type,
            period=period,
            frequency_type=frequency_type,
            frequency=frequency,
            use_cache=use_cache
        )
    
    def get_option_chain(self, symbol, **kwargs):
        """
        Get option chain data for a symbol.
        
        Args:
            symbol (str): Stock symbol
            **kwargs: Additional arguments for option chain retrieval
            
        Returns:
            dict: Option chain data
        """
        return self.historical_data.get_option_chain(symbol, **kwargs)
        
    def get_options_chain(self, symbol, **kwargs):
        """
        Alias for get_option_chain to maintain compatibility with dashboard.
        
        Args:
            symbol (str): Stock symbol
            **kwargs: Additional arguments for option chain retrieval
            
        Returns:
            dict: Option chain data
        """
        return self.get_option_chain(symbol, **kwargs)
    
    def get_quote(self, symbols):
        """
        Get quotes for one or more symbols.
        
        Args:
            symbols (str or list): Symbol or list of symbols
            
        Returns:
            dict: Quote data
        """
        return self.historical_data.get_quote(symbols)
    
    def start_streaming(self, symbols, fields=None, handlers=None):
        """
        Start streaming real-time data for specified symbols.
        
        Args:
            symbols (list): List of symbols to stream
            fields (list): List of fields to stream
            handlers (dict): Dictionary mapping data types to handler functions
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Register handlers if provided
        if handlers:
            for data_type, handler in handlers.items():
                self.realtime_data.register_handler(data_type, handler)
        
        # Start streaming
        return self.realtime_data.start_streaming(symbols, fields)
    
    def stop_streaming(self):
        """
        Stop streaming real-time data.
        
        Returns:
            bool: True if successful, False otherwise
        """
        return self.realtime_data.stop_streaming()
    
    def save_data(self, data, name, format='csv'):
        """
        Save data to file.
        
        Args:
            data (pandas.DataFrame or dict): Data to save
            name (str): Name for the saved file (without extension)
            format (str): File format ('csv', 'json', 'pickle')
            
        Returns:
            str: Path to saved file or None if failed
        """
        try:
            # Create timestamp for filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name}_{timestamp}"
            
            # Create full path
            filepath = os.path.join(self.data_directory, filename)
            
            # Save based on format
            if format == 'csv':
                if isinstance(data, pd.DataFrame):
                    full_path = f"{filepath}.csv"
                    data.to_csv(full_path, index=False)
                else:
                    full_path = f"{filepath}.csv"
                    pd.DataFrame(data).to_csv(full_path, index=False)
            elif format == 'json':
                full_path = f"{filepath}.json"
                if isinstance(data, pd.DataFrame):
                    data.to_json(full_path, orient='records')
                else:
                    import json
                    with open(full_path, 'w') as f:
                        json.dump(data, f)
            elif format == 'pickle':
                full_path = f"{filepath}.pkl"
                if isinstance(data, pd.DataFrame):
                    data.to_pickle(full_path)
                else:
                    import pickle
                    with open(full_path, 'wb') as f:
                        pickle.dump(data, f)
            else:
                logger.error(f"Unsupported format: {format}")
                return None
            
            logger.info(f"Data saved to {full_path}")
            return full_path
        
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            return None
    
    def load_data(self, filepath):
        """
        Load data from file.
        
        Args:
            filepath (str): Path to the file
            
        Returns:
            pandas.DataFrame or dict: Loaded data
        """
        try:
            # Determine format from extension
            if filepath.endswith('.csv'):
                data = pd.read_csv(filepath)
            elif filepath.endswith('.json'):
                data = pd.read_json(filepath)
            elif filepath.endswith('.pkl'):
                import pickle
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)
            else:
                logger.error(f"Unsupported file format: {filepath}")
                return None
            
            logger.info(f"Data loaded from {filepath}")
            return data
        
        except Exception as e:
            logger.error(f"Error loading data from {filepath}: {str(e)}")
            return None
