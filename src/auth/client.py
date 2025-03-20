"""
Authentication client for Schwab API.
This module handles authentication and token management for the Schwab API.
"""

import schwabdev
import os
import subprocess
import logging
from .config import SCHWAB_APP_KEY, SCHWAB_APP_SECRET, SCHWAB_CALLBACK_URL, PYTHON_EXECUTABLE

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SchwabAuthClient:
    """
    Client for authenticating with Schwab API using the schwabdev library.
    Handles token management and authentication.
    """
    
    def __init__(self, app_key=SCHWAB_APP_KEY, app_secret=SCHWAB_APP_SECRET, 
                 callback_url=SCHWAB_CALLBACK_URL, use_session=True, 
                 tokens_file=".env", capture_callback=True):
        """
        Initialize the Schwab authentication client.
        
        Args:
            app_key (str): Schwab developer app key
            app_secret (str): Schwab developer app secret
            callback_url (str): Callback URL for authentication
            use_session (bool): Whether to use a session for requests
            tokens_file (str): Path to tokens file for storing authentication tokens
            capture_callback (bool): Whether to capture callback with webserver
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.callback_url = callback_url
        self.use_session = use_session
        self.tokens_file = tokens_file
        self.capture_callback = capture_callback
        self.client = None
        
    def initialize_client(self):
        """
        Initialize the Schwab client with the provided credentials.
        
        Returns:
            schwabdev.Client: Initialized Schwab client
        """
        try:
            logger.info("Initializing Schwab client with provided credentials")
            self.client = schwabdev.Client(
                app_key=self.app_key,
                app_secret=self.app_secret,
                callback_url=self.callback_url,
                use_session=self.use_session,
                tokens_file=self.tokens_file,
                capture_callback=self.capture_callback
            )
            logger.info("Schwab client initialized successfully")
            return self.client
        except Exception as e:
            logger.error(f"Error initializing Schwab client: {str(e)}")
            raise
    
    def get_client(self):
        """
        Get the initialized Schwab client or initialize if not already done.
        
        Returns:
            schwabdev.Client: Initialized Schwab client
        """
        if self.client is None:
            return self.initialize_client()
        return self.client
    
    def check_authentication(self):
        """
        Check if the client is authenticated with Schwab API.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            client = self.get_client()
            # Try to make a simple API call to check authentication
            response = client.account_linked()
            return response is not None and len(response) > 0
        except Exception as e:
            logger.error(f"Authentication check failed: {str(e)}")
            return False
    
    def run_with_python311(self, script_path, *args):
        """
        Run a Python script with Python 3.11 (required by Schwabdev).
        
        Args:
            script_path (str): Path to the Python script
            *args: Additional arguments to pass to the script
            
        Returns:
            subprocess.CompletedProcess: Result of the subprocess run
        """
        cmd = [PYTHON_EXECUTABLE, script_path] + list(args)
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Command failed with error: {result.stderr}")
        return result
