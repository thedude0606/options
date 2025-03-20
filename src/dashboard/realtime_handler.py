"""
Real-time data handler for updating dashboard components.
This module provides callback handlers for real-time data updates.
"""

import logging
import json
import pandas as pd
from datetime import datetime
import plotly.graph_objs as go
from dash import html

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTimeHandler:
    """
    Class for handling real-time data updates and updating dashboard components.
    """
    
    def __init__(self, dashboard):
        """
        Initialize the real-time data handler.
        
        Args:
            dashboard: Dashboard instance to update
        """
        self.dashboard = dashboard
        self.data_manager = dashboard.data_manager
        self.realtime = dashboard.realtime
        self.price_data = {}
        self.volume_data = {}
        self.option_data = {}
        
        # Register callbacks with the real-time integration
        self._register_callbacks()
    
    def _register_callbacks(self):
        """
        Register callbacks with the real-time integration.
        """
        self.realtime.register_callback('QUOTE', self.handle_quote_update)
        self.realtime.register_callback('OPTION', self.handle_option_update)
    
    def handle_quote_update(self, message):
        """
        Handle quote update messages and update dashboard components.
        
        Args:
            message: Quote message from the stream
        """
        try:
            # Extract data from message
            symbol = message.get('symbol', 'UNKNOWN')
            
            # Update price data
            if symbol not in self.price_data:
                self.price_data[symbol] = []
            
            timestamp = datetime.now()
            price_point = {
                'datetime': timestamp,
                'open': message.get('openPrice', 0),
                'high': message.get('highPrice', 0),
                'low': message.get('lowPrice', 0),
                'close': message.get('lastPrice', 0),
                'volume': message.get('totalVolume', 0)
            }
            
            self.price_data[symbol].append(price_point)
            
            # Limit data points to prevent memory issues
            if len(self.price_data[symbol]) > 1000:
                self.price_data[symbol] = self.price_data[symbol][-1000:]
            
            # Update volume data
            if symbol not in self.volume_data:
                self.volume_data[symbol] = []
            
            volume_point = {
                'datetime': timestamp,
                'volume': message.get('totalVolume', 0)
            }
            
            self.volume_data[symbol].append(volume_point)
            
            # Limit data points to prevent memory issues
            if len(self.volume_data[symbol]) > 1000:
                self.volume_data[symbol] = self.volume_data[symbol][-1000:]
            
            logger.debug(f"Updated real-time data for {symbol}")
        except Exception as e:
            logger.error(f"Error handling quote update: {str(e)}")
    
    def handle_option_update(self, message):
        """
        Handle option update messages and update dashboard components.
        
        Args:
            message: Option message from the stream
        """
        try:
            # Extract data from message
            symbol = message.get('symbol', 'UNKNOWN')
            underlying = message.get('underlying', 'UNKNOWN')
            
            # Update option data
            if underlying not in self.option_data:
                self.option_data[underlying] = {}
            
            self.option_data[underlying][symbol] = {
                'timestamp': datetime.now(),
                'strike': message.get('strikePrice', 0),
                'expiration': message.get('expirationDate', ''),
                'type': 'CALL' if message.get('putCall', '') == 'CALL' else 'PUT',
                'bid': message.get('bidPrice', 0),
                'ask': message.get('askPrice', 0),
                'last': message.get('lastPrice', 0),
                'volume': message.get('totalVolume', 0),
                'openInterest': message.get('openInterest', 0),
                'delta': message.get('delta', 0),
                'gamma': message.get('gamma', 0),
                'theta': message.get('theta', 0),
                'vega': message.get('vega', 0)
            }
            
            logger.debug(f"Updated real-time option data for {symbol}")
        except Exception as e:
            logger.error(f"Error handling option update: {str(e)}")
    
    def get_real_time_price_figure(self, symbols=None):
        """
        Get a real-time price chart figure.
        
        Args:
            symbols (list): List of symbols to include in the chart
            
        Returns:
            dict: Plotly figure object
        """
        try:
            if not symbols:
                symbols = list(self.price_data.keys())
            
            if not symbols:
                return {
                    "data": [],
                    "layout": {
                        "title": "Real-time Price Chart",
                        "xaxis": {"title": "Time"},
                        "yaxis": {"title": "Price ($)"}
                    }
                }
            
            # Create traces for each symbol
            traces = []
            for symbol in symbols:
                if symbol not in self.price_data or not self.price_data[symbol]:
                    continue
                
                # Convert to DataFrame
                df = pd.DataFrame(self.price_data[symbol])
                
                traces.append(go.Scatter(
                    x=df['datetime'],
                    y=df['close'],
                    mode='lines',
                    name=symbol
                ))
            
            # Create figure
            figure = {
                "data": traces,
                "layout": {
                    "title": "Real-time Price Chart",
                    "xaxis": {"title": "Time"},
                    "yaxis": {"title": "Price ($)"},
                    "hovermode": "closest"
                }
            }
            
            return figure
        except Exception as e:
            logger.error(f"Error creating real-time price figure: {str(e)}")
            return {
                "data": [],
                "layout": {
                    "title": f"Error: {str(e)}",
                    "xaxis": {"title": "Time"},
                    "yaxis": {"title": "Price ($)"}
                }
            }
    
    def get_real_time_volume_figure(self, symbols=None):
        """
        Get a real-time volume chart figure.
        
        Args:
            symbols (list): List of symbols to include in the chart
            
        Returns:
            dict: Plotly figure object
        """
        try:
            if not symbols:
                symbols = list(self.volume_data.keys())
            
            if not symbols:
                return {
                    "data": [],
                    "layout": {
                        "title": "Real-time Volume Chart",
                        "xaxis": {"title": "Time"},
                        "yaxis": {"title": "Volume"}
                    }
                }
            
            # Create traces for each symbol
            traces = []
            for symbol in symbols:
                if symbol not in self.volume_data or not self.volume_data[symbol]:
                    continue
                
                # Convert to DataFrame
                df = pd.DataFrame(self.volume_data[symbol])
                
                traces.append(go.Bar(
                    x=df['datetime'],
                    y=df['volume'],
                    name=symbol
                ))
            
            # Create figure
            figure = {
                "data": traces,
                "layout": {
                    "title": "Real-time Volume Chart",
                    "xaxis": {"title": "Time"},
                    "yaxis": {"title": "Volume"},
                    "barmode": "group"
                }
            }
            
            return figure
        except Exception as e:
            logger.error(f"Error creating real-time volume figure: {str(e)}")
            return {
                "data": [],
                "layout": {
                    "title": f"Error: {str(e)}",
                    "xaxis": {"title": "Time"},
                    "yaxis": {"title": "Volume"}
                }
            }
    
    def get_real_time_option_table(self, symbol, option_type='both'):
        """
        Get a real-time option chain table.
        
        Args:
            symbol (str): Symbol to get option chain for
            option_type (str): Type of options to include ('calls', 'puts', 'both')
            
        Returns:
            html.Table: Formatted table for display
        """
        try:
            if symbol not in self.option_data or not self.option_data[symbol]:
                return html.Div("No real-time option data available")
            
            # Extract options
            options = self.option_data[symbol]
            
            # Create table header
            header = html.Thead(html.Tr([
                html.Th("Strike"),
                html.Th("Expiration"),
                html.Th("Type"),
                html.Th("Symbol"),
                html.Th("Bid"),
                html.Th("Ask"),
                html.Th("Last"),
                html.Th("Volume"),
                html.Th("Open Int"),
                html.Th("Delta"),
                html.Th("Gamma"),
                html.Th("Theta"),
                html.Th("Vega"),
                html.Th("Updated")
            ]))
            
            # Create table rows
            rows = []
            
            for option_symbol, option in options.items():
                # Skip if not the requested type
                if option_type == 'calls' and option['type'] != 'CALL':
                    continue
                if option_type == 'puts' and option['type'] != 'PUT':
                    continue
                
                rows.append(html.Tr([
                    html.Td(f"${option['strike']:.2f}"),
                    html.Td(option['expiration']),
                    html.Td(option['type']),
                    html.Td(option_symbol),
                    html.Td(f"${option['bid']:.2f}"),
                    html.Td(f"${option['ask']:.2f}"),
                    html.Td(f"${option['last']:.2f}"),
                    html.Td(option['volume']),
                    html.Td(option['openInterest']),
                    html.Td(f"{option['delta']:.3f}"),
                    html.Td(f"{option['gamma']:.3f}"),
                    html.Td(f"{option['theta']:.3f}"),
                    html.Td(f"{option['vega']:.3f}"),
                    html.Td(option['timestamp'].strftime("%H:%M:%S"))
                ]))
            
            # Create table body
            body = html.Tbody(rows)
            
            # Create table
            table = html.Table([header, body], className="option-table")
            
            return table
        except Exception as e:
            logger.error(f"Error creating real-time option table: {str(e)}")
            return html.Div(f"Error: {str(e)}")
