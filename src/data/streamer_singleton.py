"""
Singleton class for managing Schwab API streaming connections.
This module ensures only one streaming connection is active at a time.
"""

import logging
import threading
import asyncio
import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StreamerSingleton:
    """
    Singleton class to manage a single streaming connection.
    Ensures only one connection is active at any time.
    """
    _instance = None
    _lock = threading.RLock()  # Reentrant lock for thread safety
    _thread = None
    _event_loop = None
    _streamer = None
    _client = None
    _is_running = False
    _connection_id = None
    _last_heartbeat = 0
    _force_kill_others = True  # Flag to force kill other connections

    def __new__(cls, *args, **kwargs):
        """
        Ensure only one instance of StreamerSingleton exists.
        """
        with cls._lock:
            if cls._instance is None:
                logger.info("Creating new StreamerSingleton instance")
                cls._instance = super(StreamerSingleton, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, client=None):
        """
        Initialize the streamer singleton with a client.
        
        Args:
            client: Schwab API client
        """
        with self._lock:
            if self._initialized:
                return
                
            logger.info("Initializing streamer with provided client")
            self._client = client
            self._initialized = True
            self._is_running = False
            self._connection_id = None
            self._last_heartbeat = 0
            self._executor = ThreadPoolExecutor(max_workers=1)

    @classmethod
    def get_instance(cls, client=None):
        """
        Get the singleton instance.
        
        Args:
            client: Schwab API client (optional)
            
        Returns:
            StreamerSingleton instance
        """
        instance = cls(client)
        return instance

    def start(self):
        """
        Start the streamer in a dedicated thread.
        """
        with self._lock:
            if self._is_running:
                logger.warning("Streamer already running, not starting again")
                return
                
            logger.info("Starting streamer in dedicated thread")
            self._is_running = True
            
            # Kill any existing thread
            if self._thread is not None and self._thread.is_alive():
                logger.info("Terminating existing streamer thread")
                self._is_running = False
                self._thread.join(timeout=2.0)
            
            # Create and start new thread
            logger.info("Initializing dedicated event loop for streamer")
            self._thread = threading.Thread(target=self._run_streamer_thread, daemon=True)
            self._thread.start()
            logger.info("Streamer thread started")
            
            # Wait for initialization
            time.sleep(0.5)
            
            return self._streamer

    def _run_streamer_thread(self):
        """
        Run the streamer in a dedicated thread with its own event loop.
        """
        try:
            logger.info("Initializing streamer in dedicated event loop")
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._event_loop = loop
            
            # Initialize streamer in this thread's event loop
            try:
                if self._force_kill_others:
                    self._kill_other_connections()
                
                self._streamer = self._initialize_streamer()
                if self._streamer is None:
                    logger.error("Failed to initialize streamer")
                    self._is_running = False
                    return
                    
                # Run the event loop
                logger.info("Running streamer event loop")
                while self._is_running:
                    # Process events for a short time
                    loop.run_until_complete(asyncio.sleep(0.1))
                    
                    # Check heartbeat
                    if time.time() - self._last_heartbeat > 30:
                        logger.warning("No heartbeat received in 30 seconds, reconnecting")
                        self._reconnect()
                        
            except Exception as e:
                logger.error(f"Error initializing streamer: {str(e)}")
                self._is_running = False
                
            finally:
                # Clean up
                if loop.is_running():
                    loop.stop()
                loop.close()
                self._event_loop = None
                self._is_running = False
                logger.info("Streamer thread terminated")
                
        except Exception as e:
            logger.error(f"Error in streamer thread: {str(e)}")
            self._is_running = False

    def _initialize_streamer(self):
        """
        Initialize the streamer with the client.
        
        Returns:
            Initialized streamer object
        """
        try:
            if self._client is None:
                logger.error("Client not provided, cannot initialize streamer")
                return None
                
            # Check if client has stream attribute
            if not hasattr(self._client, 'stream'):
                logger.error("Client does not have stream attribute")
                return None
                
            # Initialize streamer
            streamer = self._client.stream
            
            # Add custom heartbeat handler
            self._add_heartbeat_handler(streamer)
            
            # Start streamer
            streamer.start()
            
            return streamer
            
        except Exception as e:
            logger.error(f"Error initializing streamer: {str(e)}")
            return None

    def _add_heartbeat_handler(self, streamer):
        """
        Add a heartbeat handler to the streamer.
        
        Args:
            streamer: Streamer object
        """
        try:
            # Check if streamer has on_message method
            if hasattr(streamer, 'on_message'):
                original_on_message = streamer.on_message
                
                def heartbeat_handler(message):
                    # Check for heartbeat
                    if isinstance(message, str):
                        try:
                            data = json.loads(message)
                            if 'notify' in data and len(data['notify']) > 0:
                                for notification in data['notify']:
                                    if 'heartbeat' in notification:
                                        self._last_heartbeat = time.time()
                                        self._connection_id = notification.get('heartbeat')
                                        logger.debug(f"Heartbeat received: {self._connection_id}")
                        except:
                            pass
                    
                    # Call original handler
                    return original_on_message(message)
                
                streamer.on_message = heartbeat_handler
                
            self._last_heartbeat = time.time()
            
        except Exception as e:
            logger.error(f"Error adding heartbeat handler: {str(e)}")

    def _reconnect(self):
        """
        Reconnect the streamer.
        """
        try:
            logger.info("Reconnecting streamer")
            
            # Stop current streamer
            if self._streamer is not None:
                try:
                    self._streamer.stop()
                except:
                    pass
                    
            # Kill other connections
            if self._force_kill_others:
                self._kill_other_connections()
                
            # Initialize new streamer
            self._streamer = self._initialize_streamer()
            if self._streamer is None:
                logger.error("Failed to reconnect streamer")
                self._is_running = False
                
            self._last_heartbeat = time.time()
            
        except Exception as e:
            logger.error(f"Error reconnecting streamer: {str(e)}")
            self._is_running = False

    def _kill_other_connections(self):
        """
        Kill other streaming connections using the same credentials.
        """
        try:
            logger.info("Attempting to kill other streaming connections")
            
            # Check if client has required attributes
            if not hasattr(self._client, 'session') or not hasattr(self._client, '_config'):
                logger.warning("Client does not have required attributes to kill other connections")
                return
                
            # Get streaming server URL
            streaming_url = self._client._config.get('streaming_api', '')
            if not streaming_url:
                logger.warning("Streaming URL not found in client config")
                return
                
            # Construct kill request URL
            kill_url = f"{streaming_url}/killconnection"
            
            # Send kill request
            try:
                response = self._client.session.post(
                    kill_url,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f"Bearer {self._client._config.get('access_token', '')}"
                    },
                    json={
                        'killAll': True
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    logger.info("Successfully killed other connections")
                    # Wait for connections to be fully terminated
                    time.sleep(1)
                else:
                    logger.warning(f"Failed to kill other connections: {response.status_code} {response.text}")
                    
            except Exception as e:
                logger.error(f"Error killing other connections: {str(e)}")
                
            # Alternative method: Use direct API call
            try:
                # Get user info
                user_info = self._client._config.get('user_info', {})
                user_id = user_info.get('user_id', '')
                
                if user_id:
                    # Construct alternative kill request
                    alt_kill_url = f"{streaming_url}/users/{user_id}/connections"
                    
                    response = self._client.session.delete(
                        alt_kill_url,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f"Bearer {self._client._config.get('access_token', '')}"
                        },
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        logger.info("Successfully killed other connections (alternative method)")
                        # Wait for connections to be fully terminated
                        time.sleep(1)
                    else:
                        logger.warning(f"Failed to kill other connections (alternative method): {response.status_code} {response.text}")
            except Exception as e:
                logger.error(f"Error killing other connections (alternative method): {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in kill_other_connections: {str(e)}")

    def stop(self):
        """
        Stop the streamer.
        """
        with self._lock:
            logger.info("Stopping streamer")
            self._is_running = False
            
            # Stop streamer
            if self._streamer is not None:
                try:
                    self._streamer.stop()
                except:
                    pass
                    
            # Wait for thread to terminate
            if self._thread is not None and self._thread.is_alive():
                self._thread.join(timeout=2.0)
                
            self._streamer = None
            self._thread = None
            self._event_loop = None
            
            logger.info("Streamer stopped")

    def get_streamer(self):
        """
        Get the streamer instance.
        
        Returns:
            Streamer instance
        """
        with self._lock:
            if not self._is_running:
                self.start()
            return self._streamer

    def is_running(self):
        """
        Check if streamer is running.
        
        Returns:
            True if running, False otherwise
        """
        with self._lock:
            return self._is_running and self._streamer is not None

    def set_client(self, client):
        """
        Set the client for the streamer.
        
        Args:
            client: Schwab API client
        """
        with self._lock:
            logger.info("Setting new client for streamer")
            self._client = client
            
            # Restart if running
            if self._is_running:
                self.stop()
                self.start()

    def __del__(self):
        """
        Clean up resources when instance is deleted.
        """
        self.stop()
