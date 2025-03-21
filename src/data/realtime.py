"""
Data retrieval module for real-time stock and options data.
This module handles streaming real-time data from the Schwab API.
"""

import logging
import json
import pandas as pd
from datetime import datetime
import traceback

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
        self.debug_mode = True  # Enable debug mode for troubleshooting
        self.initialized = False
        
    def initialize_streamer(self):
        """
        Initialize the streamer from the client.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # If already initialized, don't reinitialize
            if self.initialized and self.streamer is not None:
                logger.info("Streamer already initialized, skipping initialization")
                return True
                
            logger.info("Initializing real-time data streamer")
            
            # Check if client is properly authenticated
            if not hasattr(self.client, 'stream'):
                logger.error("Client does not have stream attribute. Authentication may have failed.")
                return False
                
            self.streamer = self.client.stream
            
            if self.streamer is None:
                logger.error("Failed to get streamer from client")
                return False
                
            self.initialized = True
            logger.info("Real-time data streamer initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing real-time data streamer: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def get_streamer(self):
        """
        Get the initialized streamer or initialize if not already done.
        
        Returns:
            schwabdev.Stream: Initialized streamer
        """
        if self.streamer is None:
            success = self.initialize_streamer()
            if not success:
                logger.error("Failed to initialize streamer")
                return None
        return self.streamer
    
    def default_handler(self, message):
        """
        Default handler for streamed data.
        
        Args:
            message (str): Message from the stream
        """
        try:
            if self.debug_mode:
                logger.info(f"Received message: {json.dumps(message, indent=2)}")
            
            # Process the message based on its content
            if isinstance(message, dict):
                # Check for Schwab API specific message structure
                if 'data' in message:
                    data = message['data']
                    if isinstance(data, list):
                        for item in data:
                            self._process_data_item(item)
                    else:
                        self._process_data_item(data)
                elif 'content' in message:
                    content = message['content']
                    if isinstance(content, list):
                        for item in content:
                            self._process_content_item(item)
                    else:
                        self._process_content_item(content)
                else:
                    # Generic message handling
                    logger.debug(f"Unrecognized message format: {message}")
            else:
                logger.debug(f"Received non-dict message: {message}")
        except Exception as e:
            logger.error(f"Error in default handler: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _process_data_item(self, item):
        """
        Process a data item from the stream.
        
        Args:
            item: Data item from the stream
        """
        try:
            if 'service' in item:
                service = item['service']
                if 'QUOTE' in service:
                    self.quote_handler(item)
                elif 'OPTION' in service:
                    self.option_handler(item)
                else:
                    logger.debug(f"Unhandled service type: {service}")
            else:
                logger.debug(f"Data item missing service field: {item}")
        except Exception as e:
            logger.error(f"Error processing data item: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _process_content_item(self, item):
        """
        Process a content item from the stream.
        
        Args:
            item: Content item from the stream
        """
        try:
            if 'service' in item:
                service = item['service']
                if 'QUOTE' in service:
                    self.quote_handler(item)
                elif 'OPTION' in service:
                    self.option_handler(item)
                else:
                    logger.debug(f"Unhandled service type: {service}")
            else:
                logger.debug(f"Content item missing service field: {item}")
        except Exception as e:
            logger.error(f"Error processing content item: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
    
    def quote_handler(self, message):
        """
        Handler for quote data.
        
        Args:
            message (str): Quote message from the stream
        """
        try:
            if self.debug_mode:
                logger.info(f"Processing quote: {json.dumps(message, indent=2)}")
            
            # Extract symbol from message based on Schwab API format
            symbol = None
            if 'key' in message:
                symbol = message['key']
            elif 'symbol' in message:
                symbol = message['symbol']
            
            if not symbol:
                logger.error("Quote message missing symbol/key field")
                return
                
            # Extract quote data based on Schwab API format
            data = {}
            data['timestamp'] = datetime.now()
            data['symbol'] = symbol
            
            # Map fields from Schwab API format
            field_mappings = {
                'lastPrice': ['lastPrice', 'last', 'last_price'],
                'bidPrice': ['bidPrice', 'bid', 'bid_price'],
                'askPrice': ['askPrice', 'ask', 'ask_price'],
                'totalVolume': ['totalVolume', 'volume', 'total_volume'],
                'openPrice': ['openPrice', 'open', 'open_price'],
                'highPrice': ['highPrice', 'high', 'high_price'],
                'lowPrice': ['lowPrice', 'low', 'low_price']
            }
            
            # Try to extract fields using different possible field names
            for target_field, possible_fields in field_mappings.items():
                for field in possible_fields:
                    if field in message:
                        data[target_field] = message[field]
                        break
                if target_field not in data:
                    data[target_field] = 0
            
            # Call any registered callbacks for this data type
            if 'QUOTE' in self.data_handlers:
                for callback in self.data_handlers['QUOTE']:
                    callback(data)
                    
            logger.debug(f"Successfully processed quote for {symbol}")
        except Exception as e:
            logger.error(f"Error in quote handler: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
    
    def option_handler(self, message):
        """
        Handler for option data.
        
        Args:
            message (str): Option message from the stream
        """
        try:
            if self.debug_mode:
                logger.info(f"Processing option data: {json.dumps(message, indent=2)}")
            
            # Extract symbol from message based on Schwab API format
            symbol = None
            underlying = None
            
            if 'key' in message:
                symbol = message['key']
            elif 'symbol' in message:
                symbol = message['symbol']
                
            if 'underlying' in message:
                underlying = message['underlying']
            elif 'underlyingSymbol' in message:
                underlying = message['underlyingSymbol']
            
            if not symbol:
                logger.error("Option message missing symbol/key field")
                return
                
            if not underlying:
                # Try to extract underlying from option symbol
                parts = symbol.split('_')
                if len(parts) > 0:
                    underlying = parts[0]
                else:
                    logger.warning(f"Could not determine underlying for option {symbol}")
                    underlying = "UNKNOWN"
            
            # Extract option data based on Schwab API format
            data = {}
            data['timestamp'] = datetime.now()
            data['symbol'] = symbol
            data['underlying'] = underlying
            
            # Map fields from Schwab API format
            field_mappings = {
                'strikePrice': ['strikePrice', 'strike', 'strike_price'],
                'expirationDate': ['expirationDate', 'expiration', 'expiration_date'],
                'putCall': ['putCall', 'option_type', 'type'],
                'bidPrice': ['bidPrice', 'bid', 'bid_price'],
                'askPrice': ['askPrice', 'ask', 'ask_price'],
                'lastPrice': ['lastPrice', 'last', 'last_price'],
                'totalVolume': ['totalVolume', 'volume', 'total_volume'],
                'openInterest': ['openInterest', 'open_interest'],
                'delta': ['delta'],
                'gamma': ['gamma'],
                'theta': ['theta'],
                'vega': ['vega'],
                'rho': ['rho']
            }
            
            # Try to extract fields using different possible field names
            for target_field, possible_fields in field_mappings.items():
                for field in possible_fields:
                    if field in message:
                        data[target_field] = message[field]
                        break
                if target_field not in data:
                    data[target_field] = 0 if target_field not in ['expirationDate', 'putCall'] else ''
            
            # Call any registered callbacks for this data type
            if 'OPTION' in self.data_handlers:
                for callback in self.data_handlers['OPTION']:
                    callback(data)
                    
            logger.debug(f"Successfully processed option data for {symbol}")
        except Exception as e:
            logger.error(f"Error in option handler: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
    
    def register_handler(self, data_type, callback):
        """
        Register a handler for a specific data type.
        
        Args:
            data_type (str): Type of data to handle ('QUOTE', 'OPTION', etc.)
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
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def start_streaming(self, symbols=None, fields=None, handler=None):
        """
        Start streaming real-time data for specified symbols.
        
        Args:
            symbols (list): List of symbols to stream
            fields (list): List of fields to stream
            handler (function): Handler function for streamed data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Initialize streamer if not already done
            if not self.initialize_streamer():
                logger.error("Failed to initialize streamer")
                return False
            
            # Register handler if provided
            if handler:
                self.streamer.add_handler(handler)
            
            # Check if symbols are provided
            if not symbols:
                logger.warning("No symbols provided for streaming")
                return False
            
            # Find appropriate subscription method
            subscription_methods = [
                'level_one_equities',
                'level_one_options',
                'quote'
            ]
            
            method_found = False
            for method_name in subscription_methods:
                if hasattr(self.streamer, method_name):
                    method = getattr(self.streamer, method_name)
                    logger.info(f"Using {method_name} method for subscription")
                    
                    try:
                        # Subscribe to symbols
                        method(symbols=symbols, fields=fields)
                        method_found = True
                        break
                    except Exception as e:
                        logger.error(f"Error using {method_name} method: {str(e)}")
                        if self.debug_mode:
                            logger.error(f"Traceback: {traceback.format_exc()}")
            
            if not method_found:
                # Fallback to generic subscription
                logger.warning(f"Could not find appropriate subscription method. Available methods: {dir(self.streamer)}")
                
                for symbol in symbols:
                    logger.info(f"Attempting generic subscription for {symbol}")
                    try:
                        # Try to use a generic method if available
                        if hasattr(self.streamer, 'start'):
                            self.streamer.start(handler or self.default_handler)
                        elif hasattr(self.streamer, 'start_auto'):
                            self.streamer.start_auto()
                        
                        logger.info(f"Started generic streaming for {symbol}")
                    except Exception as e:
                        logger.error(f"Error starting generic streaming for {symbol}: {str(e)}")
                        if self.debug_mode:
                            logger.error(f"Traceback: {traceback.format_exc()}")
                        return False
            
            # Update active subscriptions
            self.active_subscriptions.update(symbols)
            
            logger.info(f"Started streaming real-time data for symbols: {symbols}")
            return True
        except Exception as e:
            logger.error(f"Error starting real-time data streaming: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def stop_streaming(self):
        """
        Stop streaming real-time data.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.streamer:
                logger.warning("No active streamer to stop")
                return False
            
            # Stop streaming
            if hasattr(self.streamer, 'stop'):
                self.streamer.stop()
                logger.info("Stopped streaming real-time data")
                self.active_subscriptions.clear()
                return True
            else:
                logger.error("Streamer does not have stop method")
                return False
        except Exception as e:
            logger.error(f"Error stopping real-time data streaming: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
            return False
