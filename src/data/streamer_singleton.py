"""
Singleton streamer module to ensure only one streaming connection is active.
This module provides a singleton wrapper around the real-time data streamer.
"""

import logging
from src.data.realtime import RealTimeDataStreamer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StreamerSingleton:
    """
    Singleton class to ensure only one streaming connection is active at a time.
    """
    _instance = None
    _streamer = None
    _initialized = False
    
    @classmethod
    def get_instance(cls, client=None):
        """
        Get the singleton instance of the streamer.
        
        Args:
            client: Schwab client to use for initialization (only used if not already initialized)
            
        Returns:
            RealTimeDataStreamer: Singleton instance of the real-time data streamer
        """
        if cls._instance is None:
            logger.info("Creating new StreamerSingleton instance")
            cls._instance = cls()
            
        if client is not None and not cls._initialized:
            logger.info("Initializing streamer with provided client")
            cls._streamer = RealTimeDataStreamer(client)
            cls._initialized = True
            
        return cls._streamer
    
    @classmethod
    def is_initialized(cls):
        """
        Check if the streamer is initialized.
        
        Returns:
            bool: True if initialized, False otherwise
        """
        return cls._initialized
    
    @classmethod
    def reset(cls):
        """
        Reset the singleton instance.
        This is primarily for testing purposes.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if cls._streamer is not None:
                cls._streamer.stop_streaming()
            cls._instance = None
            cls._streamer = None
            cls._initialized = False
            logger.info("StreamerSingleton has been reset")
            return True
        except Exception as e:
            logger.error(f"Error resetting StreamerSingleton: {str(e)}")
            return False
