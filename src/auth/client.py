"""
Authentication client for Schwab API.
This module handles authentication and token management for the Schwab API.
"""

import schwabdev

class SchwabAuthClient:
    """
    Client for authenticating with Schwab API using the schwabdev library.
    Handles token management and authentication.
    """
    
    def __init__(self, app_key, app_secret, callback_url, use_session=True):
        """
        Initialize the Schwab authentication client.
        
        Args:
            app_key (str): Schwab developer app key
            app_secret (str): Schwab developer app secret
            callback_url (str): Callback URL for authentication
            use_session (bool): Whether to use a session for requests
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.callback_url = callback_url
        self.use_session = use_session
        self.client = None
        
    def initialize_client(self):
        """
        Initialize the Schwab client with the provided credentials.
        
        Returns:
            schwabdev.Client: Initialized Schwab client
        """
        self.client = schwabdev.Client(
            app_key=self.app_key,
            app_secret=self.app_secret,
            callback_url=self.callback_url,
            use_session=self.use_session
        )
        return self.client
    
    def get_client(self):
        """
        Get the initialized Schwab client or initialize if not already done.
        
        Returns:
            schwabdev.Client: Initialized Schwab client
        """
        if self.client is None:
            return self.initialize_client()
        return self.client
