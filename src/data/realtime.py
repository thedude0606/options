"""
Data retrieval module for real-time stock and options data.
This module handles streaming real-time data from the Schwab API.
"""

import logging
import json
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTimeDataStreamer:
    """
    Class for streaming real-time stock and options data from Schwab API.
    """
    
    def __init__(self, client):
        """
        Initialize the real-time data streamer.
        
        Args:
            client (schwabdev.Client): Initialized Schwab client
        """
        self.client = client
        self.streamer = None
        self.active_subscriptions = set()
        self.data_handlers = {}
        
    def initialize_streamer(self):
        """
        Initialize the streamer from the client.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Initializing real-time data streamer")
            self.streamer = self.client.stream
            logger.info("Real-time data streamer initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing real-time data streamer: {str(e)}")
            return False
    
    def get_streamer(self):
        """
        Get the initialized streamer or initialize if not already done.
        
        Returns:
            schwabdev.Stream: Initialized streamer
        """
        if self.streamer is None:
            self.initialize_streamer()
        return self.streamer
    
    def default_handler(self, message):
        """
        Default handler for streamed data.
        
        Args:
            message (str): Message from the stream
        """
        try:
            logger.debug(f"Received message: {message}")
            # Process the message based on its content
            # This is a simple example that just prints the message
            print(f"Received: {message}")
        except Exception as e:
            logger.error(f"Error in default handler: {str(e)}")
    
    def quote_handler(self, message):
        """
        Handler for quote data.
        
        Args:
            message (str): Quote message from the stream
        """
        try:
            # Parse the message and extract quote data
            # This would be customized based on the actual message format
            logger.debug(f"Received quote: {message}")
            
            # Example processing (adjust based on actual data format)
            data = {
                'timestamp': datetime.now(),
                'symbol': message.get('symbol', 'UNKNOWN'),
                'price': message.get('price', 0.0),
                'bid': message.get('bid', 0.0),
                'ask': message.get('ask', 0.0),
                'volume': message.get('volume', 0)
            }
            
            # Call any registered callbacks for this data type
            if 'QUOTE' in self.data_handlers:
                for callback in self.data_handlers['QUOTE']:
                    callback(data)
        except Exception as e:
            logger.error(f"Error in quote handler: {str(e)}")
    
    def option_handler(self, message):
        """
        Handler for option data.
        
        Args:
            message (str): Option message from the stream
        """
        try:
            # Parse the message and extract option data
            logger.debug(f"Received option data: {message}")
            
            # Example processing (adjust based on actual data format)
            data = {
                'timestamp': datetime.now(),
                'symbol': message.get('symbol', 'UNKNOWN'),
                'strike': message.get('strike', 0.0),
                'expiration': message.get('expiration', ''),
                'type': message.get('type', ''),
                'bid': message.get('bid', 0.0),
                'ask': message.get('ask', 0.0),
                'last': message.get('last', 0.0),
                'volume': message.get('volume', 0),
                'open_interest': message.get('openInterest', 0)
            }
            
            # Call any registered callbacks for this data type
            if 'OPTION' in self.data_handlers:
                for callback in self.data_handlers['OPTION']:
                    callback(data)
        except Exception as e:
            logger.error(f"Error in option handler: {str(e)}")
    
    def register_handler(self, data_type, callback):
        """
        Register a callback function for a specific data type.
        
        Args:
            data_type (str): Type of data ('QUOTE', 'OPTION', etc.)
            callback (function): Callback function to handle the data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if data_type not in self.data_handlers:
                self.data_handlers[data_type] = []
            
            self.data_handlers[data_type].append(callback)
            logger.info(f"Registered handler for {data_type} data")
            return True
        except Exception as e:
            logger.error(f"Error registering handler for {data_type} data: {str(e)}")
            return False
    
    def start_streaming(self, symbols=None, fields=None, handler=None):
        """
        Start streaming real-time data.
        
        Args:
            symbols (list): List of symbols to stream
            fields (list): List of fields to stream
            handler (function): Handler function for the streamed data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            streamer = self.get_streamer()
            
            if streamer is None:
                logger.error("Failed to initialize streamer")
                return False
            
            # Use default handler if none provided
            if handler is None:
                handler = self.default_handler
            
            # Start the streamer with the provided handler
            streamer.start(handler)
            
            # Add subscriptions if symbols are provided
            if symbols:
                self.add_subscriptions(symbols, fields)
            
            logger.info("Started streaming real-time data")
            return True
        except Exception as e:
            logger.error(f"Error starting real-time data streaming: {str(e)}")
            return False
    
    def add_subscriptions(self, symbols, fields=None):
        """
        Add subscriptions to the streamer.
        
        Args:
            symbols (list): List of symbols to subscribe to
            fields (list): List of fields to subscribe to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            streamer = self.get_streamer()
            
            if streamer is None:
                logger.error("Failed to initialize streamer")
                return False
            
            # Default fields if none provided
            if fields is None:
                fields = ['QUOTE']
            
            # Add each symbol to the subscription
            for symbol in symbols:
                for field in fields:
                    subscription = f"{symbol}_{field}"
                    if subscription not in self.active_subscriptions:
                        # Add subscription based on field type
                        if field == 'QUOTE':
                            streamer.add_quote_subscription(symbol)
                        elif field == 'OPTION':
                            streamer.add_option_subscription(symbol)
                        # Add more field types as needed
                        
                        self.active_subscriptions.add(subscription)
                        logger.info(f"Added subscription for {symbol} {field}")
            
            return True
        except Exception as e:
            logger.error(f"Error adding subscriptions: {str(e)}")
            return False
    
    def stop_streaming(self):
        """
        Stop streaming real-time data.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            streamer = self.get_streamer()
            
            if streamer is None:
                logger.error("No active streamer to stop")
                return False
            
            # Stop the streamer
            streamer.stop()
            
            # Clear active subscriptions
            self.active_subscriptions.clear()
            
            logger.info("Stopped streaming real-time data")
            return True
        except Exception as e:
            logger.error(f"Error stopping real-time data streaming: {str(e)}")
            return False
