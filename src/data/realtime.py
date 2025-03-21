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
        
    def initialize_streamer(self):
        """
        Initialize the streamer from the client.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Initializing real-time data streamer")
            
            # Check if client is properly authenticated
            if not hasattr(self.client, 'stream'):
                logger.error("Client does not have stream attribute. Authentication may have failed.")
                return False
                
            self.streamer = self.client.stream
            
            if self.streamer is None:
                logger.error("Failed to get streamer from client")
                return False
                
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
                'openInterest': ['openInterest', 'open_interest'],
                'volatility': ['volatility', 'implied_volatility'],
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
                    data[target_field] = 0
            
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
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def start_streaming(self, symbols=None, fields=None, handler=None):
        """
        Start streaming real-time data.
        
        Args:
            symbols (list): List of symbols to stream
            fields (list): List of fields to stream
            handler (function): Handler function for the stream
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if symbols is None:
                symbols = []
            
            # Register handler if provided
            if handler is not None:
                for field in fields if fields else ['QUOTE']:
                    self.register_handler(field, handler)
            
            # Get streamer
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
                        try:
                            # Add subscription based on field type
                            if field == 'QUOTE':
                                # Use the correct method for subscribing to quotes
                                # Based on Schwabdev documentation, we should use a method like this:
                                try:
                                    # Try the most likely method names based on documentation
                                    if hasattr(streamer, 'level_one_equity_subs'):
                                        streamer.level_one_equity_subs([symbol])
                                        logger.info(f"Added quote subscription for {symbol} using level_one_equity_subs")
                                    elif hasattr(streamer, 'quote_subs'):
                                        streamer.quote_subs([symbol])
                                        logger.info(f"Added quote subscription for {symbol} using quote_subs")
                                    elif hasattr(streamer, 'add_level_one_equity_handler'):
                                        # If we have a handler method, we might need to register the handler first
                                        streamer.add_level_one_equity_handler(self.quote_handler)
                                        streamer.level_one_equity_subs([symbol])
                                        logger.info(f"Added quote subscription for {symbol} using add_level_one_equity_handler")
                                    else:
                                        # If we can't find the right method, log the available methods
                                        available_methods = [method for method in dir(streamer) if not method.startswith('_')]
                                        logger.warning(f"Could not find appropriate subscription method. Available methods: {available_methods}")
                                        logger.info(f"Attempting generic subscription for {symbol}")
                                        # Try a generic subscription approach
                                        if hasattr(streamer, 'start'):
                                            streamer.start(self.default_handler)
                                            logger.info(f"Started generic streaming for {symbol}")
                                except Exception as e:
                                    logger.error(f"Error adding quote subscription for {symbol}: {str(e)}")
                                    if self.debug_mode:
                                        logger.error(f"Traceback: {traceback.format_exc()}")
                            elif field == 'OPTION':
                                # Use the correct method for subscribing to options
                                try:
                                    # Try the most likely method names based on documentation
                                    if hasattr(streamer, 'level_one_option_subs'):
                                        streamer.level_one_option_subs([symbol])
                                        logger.info(f"Added option subscription for {symbol} using level_one_option_subs")
                                    elif hasattr(streamer, 'option_subs'):
                                        streamer.option_subs([symbol])
                                        logger.info(f"Added option subscription for {symbol} using option_subs")
                                    elif hasattr(streamer, 'add_level_one_option_handler'):
                                        # If we have a handler method, we might need to register the handler first
                                        streamer.add_level_one_option_handler(self.option_handler)
                                        streamer.level_one_option_subs([symbol])
                                        logger.info(f"Added option subscription for {symbol} using add_level_one_option_handler")
                                    else:
                                        # If we can't find the right method, log the available methods
                                        available_methods = [method for method in dir(streamer) if not method.startswith('_')]
                                        logger.warning(f"Could not find appropriate subscription method. Available methods: {available_methods}")
                                        logger.info(f"Attempting generic subscription for {symbol}")
                                        # Try a generic subscription approach
                                        if hasattr(streamer, 'start'):
                                            streamer.start(self.default_handler)
                                            logger.info(f"Started generic streaming for {symbol}")
                                except Exception as e:
                                    logger.error(f"Error adding option subscription for {symbol}: {str(e)}")
                                    if self.debug_mode:
                                        logger.error(f"Traceback: {traceback.format_exc()}")
                            # Add more field types as needed
                            
                            self.active_subscriptions.add(subscription)
                        except Exception as e:
                            logger.error(f"Error adding subscription for {symbol} {field}: {str(e)}")
                            if self.debug_mode:
                                logger.error(f"Traceback: {traceback.format_exc()}")
                            continue
            
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
            streamer = self.get_streamer()
            
            if streamer is None:
                logger.error("Failed to get streamer")
                return False
            
            # Stop streaming
            if hasattr(streamer, 'stop'):
                streamer.stop()
            elif hasattr(streamer, 'disconnect'):
                streamer.disconnect()
            
            self.active_subscriptions = set()
            logger.info("Stopped streaming real-time data")
            return True
        except Exception as e:
            logger.error(f"Error stopping real-time data streaming: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
            return False
