"""
Singleton streamer module to ensure only one streaming connection is active.
This module provides a singleton wrapper around the real-time data streamer
with proper asyncio event loop handling.
"""

import logging
import asyncio
import threading
import time
from src.data.realtime import RealTimeDataStreamer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StreamerSingleton:
    """
    Singleton class to ensure only one streaming connection is active at a time.
    Handles asyncio event loop conflicts properly.
    """
    _instance = None
    _streamer = None
    _initialized = False
    _lock = threading.Lock()
    _event_loop = None
    _thread = None
    _running = False
    _client = None
    _thread_id = None
    
    @classmethod
    def get_instance(cls, client=None):
        """
        Get the singleton instance of the streamer.
        
        Args:
            client: Schwab client to use for initialization (only used if not already initialized)
            
        Returns:
            RealTimeDataStreamer: Singleton instance of the real-time data streamer
        """
        with cls._lock:
            if cls._instance is None:
                logger.info("Creating new StreamerSingleton instance")
                cls._instance = cls()
            
            # Store the client reference for potential reconnection
            if client is not None:
                cls._client = client
                
            # Only initialize if not already initialized or if we need to reinitialize with a new client
            if client is not None and not cls._initialized:
                logger.info("Initializing streamer with provided client")
                # Create the streamer but don't start it yet
                cls._streamer = RealTimeDataStreamer(client)
                cls._initialized = True
                
                # Start the streamer in a dedicated thread with its own event loop
                if not cls._running:
                    cls._start_streamer_thread()
            
            return cls._streamer
    
    @classmethod
    def _start_streamer_thread(cls):
        """
        Start the streamer in a dedicated thread with its own event loop.
        This prevents asyncio event loop conflicts.
        """
        try:
            # If there's already a thread running, stop it first
            if cls._running and cls._thread and cls._thread.is_alive():
                logger.info("Stopping existing streamer thread before starting a new one")
                cls.reset()
                
            # Wait a moment to ensure any previous threads are fully stopped
            time.sleep(0.5)
                
            logger.info("Starting streamer in dedicated thread")
            cls._running = True
            cls._thread = threading.Thread(target=cls._run_streamer_loop, daemon=True)
            cls._thread.start()
            cls._thread_id = cls._thread.ident
            logger.info(f"Streamer thread started with ID: {cls._thread_id}")
        except Exception as e:
            logger.error(f"Error starting streamer thread: {str(e)}")
            cls._running = False
    
    @classmethod
    def _run_streamer_loop(cls):
        """
        Run the streamer in a dedicated event loop.
        """
        try:
            logger.info("Initializing dedicated event loop for streamer")
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            cls._event_loop = loop
            
            # Initialize the streamer's client connection in this loop
            if hasattr(cls._streamer, 'initialize_streamer'):
                logger.info("Initializing streamer in dedicated event loop")
                try:
                    # Use run_until_complete with a timeout to prevent hanging
                    future = asyncio.ensure_future(cls._async_initialize_streamer(), loop=loop)
                    loop.run_until_complete(asyncio.wait_for(future, timeout=10.0))
                except asyncio.TimeoutError:
                    logger.error("Timeout while initializing streamer")
                except Exception as e:
                    logger.error(f"Error initializing streamer in event loop: {str(e)}")
            
            # Keep the loop running to handle streaming events
            logger.info("Running streamer event loop")
            loop.run_forever()
        except Exception as e:
            logger.error(f"Error in streamer thread: {str(e)}")
        finally:
            logger.info("Streamer thread exiting")
            cls._running = False
            if cls._event_loop:
                try:
                    # Close all running tasks
                    pending = asyncio.all_tasks(loop=cls._event_loop)
                    for task in pending:
                        task.cancel()
                    
                    # Run the event loop until all tasks are cancelled
                    if pending:
                        cls._event_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    
                    cls._event_loop.close()
                except Exception as e:
                    logger.error(f"Error closing event loop: {str(e)}")
    
    @classmethod
    async def _async_initialize_streamer(cls):
        """
        Initialize the streamer asynchronously.
        """
        try:
            # Get the streamer's underlying client
            if hasattr(cls._streamer, 'get_streamer'):
                streamer = cls._streamer.get_streamer()
                if streamer and hasattr(streamer, 'start'):
                    # Register the default handler
                    await streamer.start(cls._streamer.default_handler)
                    logger.info("Streamer initialized successfully in dedicated event loop")
                else:
                    logger.error("Streamer does not have start method")
            else:
                logger.error("Streamer does not have get_streamer method")
        except Exception as e:
            logger.error(f"Error initializing streamer: {str(e)}")
    
    @classmethod
    def is_initialized(cls):
        """
        Check if the streamer is initialized.
        
        Returns:
            bool: True if initialized, False otherwise
        """
        return cls._initialized
    
    @classmethod
    def is_running(cls):
        """
        Check if the streamer thread is running.
        
        Returns:
            bool: True if running, False otherwise
        """
        return cls._running and cls._thread and cls._thread.is_alive()
    
    @classmethod
    def reset(cls):
        """
        Reset the singleton instance.
        This is primarily for testing purposes.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with cls._lock:
                # First stop the streamer
                if cls._streamer is not None:
                    try:
                        cls._streamer.stop_streaming()
                    except Exception as e:
                        logger.error(f"Error stopping streamer: {str(e)}")
                
                # Then stop the event loop
                if cls._event_loop and cls._event_loop.is_running():
                    try:
                        # Use call_soon_threadsafe to stop the loop from another thread
                        cls._event_loop.call_soon_threadsafe(cls._event_loop.stop)
                    except Exception as e:
                        logger.error(f"Error stopping event loop: {str(e)}")
                
                # Wait for the thread to join
                if cls._thread and cls._thread.is_alive():
                    try:
                        cls._thread.join(timeout=2.0)
                        if cls._thread.is_alive():
                            logger.warning("Thread did not terminate within timeout")
                    except Exception as e:
                        logger.error(f"Error joining thread: {str(e)}")
                
                # Reset all class variables
                cls._instance = None
                cls._streamer = None
                cls._initialized = False
                cls._running = False
                cls._event_loop = None
                cls._thread = None
                cls._thread_id = None
                
                # Wait a moment to ensure resources are released
                time.sleep(0.5)
                
                logger.info("StreamerSingleton has been reset")
                return True
        except Exception as e:
            logger.error(f"Error resetting StreamerSingleton: {str(e)}")
            return False
    
    @classmethod
    def register_handler(cls, data_type, callback):
        """
        Register a handler for a specific data type.
        This is a proxy method to the underlying streamer.
        
        Args:
            data_type (str): Type of data to handle
            callback (function): Callback function to handle the data
            
        Returns:
            bool: True if successful, False otherwise
        """
        if cls._streamer:
            return cls._streamer.register_handler(data_type, callback)
        return False
    
    @classmethod
    def start_streaming(cls, symbols=None, fields=None, handlers=None):
        """
        Start streaming for specific symbols.
        This is a proxy method to the underlying streamer.
        
        Args:
            symbols (list): List of symbols to stream
            fields (list): List of fields to stream
            handlers (dict): Dictionary of handlers for different data types
            
        Returns:
            bool: True if successful, False otherwise
        """
        if cls._streamer:
            # Register handlers if provided
            if handlers:
                for data_type, handler in handlers.items():
                    cls._streamer.register_handler(data_type, handler)
            
            # Start streaming in the dedicated thread
            if cls._running and cls._thread and cls._thread.is_alive():
                # The actual streaming is handled by the dedicated thread
                # We need to pass the symbols to the streamer
                if symbols:
                    # Call the streamer's start_streaming method
                    return cls._streamer.start_streaming(symbols=symbols, fields=fields)
                return True
            else:
                # If thread is not running, try to restart it
                logger.warning("Streamer thread not running, attempting to restart")
                cls._start_streamer_thread()
                # Wait a moment for the thread to start
                time.sleep(1.0)
                if cls._running and cls._thread and cls._thread.is_alive():
                    # Now try to start streaming
                    if symbols:
                        return cls._streamer.start_streaming(symbols=symbols, fields=fields)
                    return True
                else:
                    logger.error("Failed to restart streamer thread")
                    return False
        return False
    
    @classmethod
    def stop_streaming(cls):
        """
        Stop streaming.
        This is a proxy method to the underlying streamer.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if cls._streamer:
            return cls._streamer.stop_streaming()
        return False
