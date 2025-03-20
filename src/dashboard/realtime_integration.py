"""
Real-time data integration module for the dashboard.
This module enhances the dashboard with real-time data streaming capabilities.
"""

import logging
import json
import pandas as pd
from datetime import datetime
import threading
import time
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTimeIntegration:
    """
    Class for integrating real-time data into the dashboard.
    """
    
    def __init__(self, data_manager, update_interval=5):
        """
        Initialize the real-time data integration.
        
        Args:
            data_manager: Data manager instance for retrieving data
            update_interval (int): Update interval in seconds
        """
        self.data_manager = data_manager
        self.update_interval = update_interval
        self.streaming_active = False
        self.streaming_thread = None
        self.streaming_symbols = []
        self.data_callbacks = {}
        self.last_update = {}
        self.debug_mode = True  # Enable debug mode for troubleshooting
    
    def register_callback(self, data_type, callback):
        """
        Register a callback function for a specific data type.
        
        Args:
            data_type (str): Type of data ('QUOTE', 'OPTION', etc.)
            callback (function): Callback function to handle the data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if data_type not in self.data_callbacks:
                self.data_callbacks[data_type] = []
            
            self.data_callbacks[data_type].append(callback)
            logger.info(f"Registered callback for {data_type} data")
            return True
        except Exception as e:
            logger.error(f"Error registering callback for {data_type} data: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def handle_quote_update(self, message):
        """
        Handle quote update messages from the streamer.
        
        Args:
            message: Quote message from the stream
        """
        try:
            if self.debug_mode:
                logger.info(f"Processing quote update: {json.dumps(message, indent=2)}")
                
            # Process the message and extract relevant data
            symbol = message.get('symbol', 'UNKNOWN')
            
            if symbol == 'UNKNOWN' and 'key' in message:
                symbol = message['key']
                
            if symbol == 'UNKNOWN':
                logger.warning(f"Quote update missing symbol: {message}")
                return
            
            # Update last update time
            self.last_update[symbol] = datetime.now()
            
            # Call registered callbacks
            if 'QUOTE' in self.data_callbacks:
                for callback in self.data_callbacks['QUOTE']:
                    callback(message)
            
            logger.debug(f"Processed quote update for {symbol}")
        except Exception as e:
            logger.error(f"Error handling quote update: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.error(f"Message that caused error: {message}")
    
    def handle_option_update(self, message):
        """
        Handle option update messages from the streamer.
        
        Args:
            message: Option message from the stream
        """
        try:
            if self.debug_mode:
                logger.info(f"Processing option update: {json.dumps(message, indent=2)}")
                
            # Process the message and extract relevant data
            symbol = message.get('symbol', 'UNKNOWN')
            underlying = message.get('underlying', 'UNKNOWN')
            
            if symbol == 'UNKNOWN' and 'key' in message:
                symbol = message['key']
                
            if symbol == 'UNKNOWN':
                logger.warning(f"Option update missing symbol: {message}")
                return
                
            if underlying == 'UNKNOWN':
                # Try to extract underlying from option symbol
                parts = symbol.split('_')
                if len(parts) > 0:
                    underlying = parts[0]
                else:
                    logger.warning(f"Could not determine underlying for option {symbol}")
            
            # Update last update time
            self.last_update[symbol] = datetime.now()
            
            # Call registered callbacks
            if 'OPTION' in self.data_callbacks:
                for callback in self.data_callbacks['OPTION']:
                    callback(message)
            
            logger.debug(f"Processed option update for {symbol}")
        except Exception as e:
            logger.error(f"Error handling option update: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.error(f"Message that caused error: {message}")
    
    def start_streaming(self, symbols, fields=None):
        """
        Start streaming real-time data for specified symbols.
        
        Args:
            symbols (list): List of symbols to stream
            fields (list): List of fields to stream
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.streaming_active:
                logger.warning("Real-time streaming is already active")
                return False
            
            self.streaming_symbols = symbols
            
            # Define the message handler
            def message_handler(message):
                try:
                    if self.debug_mode:
                        logger.info(f"Received message: {json.dumps(message, indent=2)}")
                        
                    # Determine message type and route to appropriate handler
                    if isinstance(message, dict):
                        # Check for Schwab API specific message structure
                        if 'data' in message:
                            data = message['data']
                            if isinstance(data, list):
                                for item in data:
                                    self._process_data_item(item)
                            else:
                                self._process_data_item(data)
                        elif 'content' in message and isinstance(message['content'], list):
                            for content_item in message['content']:
                                if 'service' in content_item:
                                    service = content_item.get('service', '')
                                    if 'QUOTE' in service:
                                        self.handle_quote_update(content_item)
                                    elif 'OPTION' in service:
                                        self.handle_option_update(content_item)
                        else:
                            logger.debug(f"Unrecognized message format: {message}")
                    else:
                        logger.debug(f"Received non-dict message: {message}")
                except Exception as e:
                    logger.error(f"Error in message handler: {str(e)}")
                    if self.debug_mode:
                        logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Start streaming with the data manager
            success = self.data_manager.realtime_data.start_streaming(
                symbols=symbols,
                fields=fields,
                handler=message_handler
            )
            
            if success:
                self.streaming_active = True
                
                # Start monitoring thread
                self.streaming_thread = threading.Thread(
                    target=self._monitor_streaming,
                    daemon=True
                )
                self.streaming_thread.start()
                
                logger.info(f"Started real-time streaming for {', '.join(symbols)}")
                return True
            else:
                logger.error("Failed to start real-time streaming")
                return False
        except Exception as e:
            logger.error(f"Error starting real-time streaming: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
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
                    self.handle_quote_update(item)
                elif 'OPTION' in service:
                    self.handle_option_update(item)
                else:
                    logger.debug(f"Unhandled service type: {service}")
            else:
                logger.debug(f"Data item missing service field: {item}")
        except Exception as e:
            logger.error(f"Error processing data item: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
    
    def stop_streaming(self):
        """
        Stop streaming real-time data.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.streaming_active:
                logger.warning("Real-time streaming is not active")
                return False
            
            # Stop streaming with the data manager
            success = self.data_manager.realtime_data.stop_streaming()
            
            if success:
                self.streaming_active = False
                self.streaming_symbols = []
                self.last_update = {}
                
                logger.info("Stopped real-time streaming")
                return True
            else:
                logger.error("Failed to stop real-time streaming")
                return False
        except Exception as e:
            logger.error(f"Error stopping real-time streaming: {str(e)}")
            if self.debug_mode:
                logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _monitor_streaming(self):
        """
        Monitor the streaming connection and handle reconnection if needed.
        """
        while self.streaming_active:
            try:
                # Check if we've received updates for all symbols recently
                current_time = datetime.now()
                for symbol in self.streaming_symbols:
                    if symbol not in self.last_update:
                        logger.warning(f"No updates received yet for {symbol}")
                        continue
                    
                    last_update_time = self.last_update.get(symbol)
                    if last_update_time and (current_time - last_update_time).seconds > 60:
                        logger.warning(f"No updates received for {symbol} in the last minute")
                        
                        # Attempt to restart streaming
                        logger.info("Attempting to restart streaming")
                        self.data_manager.realtime_data.stop_streaming()
                        time.sleep(1)
                        self.data_manager.realtime_data.start_streaming(
                            symbols=self.streaming_symbols
                        )
                        break
                
                # Sleep for a while before checking again
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in streaming monitor: {str(e)}")
                if self.debug_mode:
                    logger.error(f"Traceback: {traceback.format_exc()}")
                time.sleep(self.update_interval)
    
    def get_streaming_status(self):
        """
        Get the current streaming status.
        
        Returns:
            dict: Dictionary with streaming status information
        """
        status = {
            "active": self.streaming_active,
            "symbols": self.streaming_symbols,
            "last_updates": {}
        }
        
        # Add last update times
        for symbol, update_time in self.last_update.items():
            status["last_updates"][symbol] = update_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return status
