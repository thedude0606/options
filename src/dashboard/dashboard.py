"""
Dashboard module for visualizing stock and options data.
This module provides the main dashboard interface for the application.
"""

import logging
import dash
from dash import dcc, html, callback, Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import os
from .utils import create_candlestick_chart, format_option_chain_table, create_data_table, get_expiration_dates
from .realtime_integration import RealTimeIntegration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Dashboard:
    """
    Class for creating and managing the dashboard interface.
    """
    
    def __init__(self, data_manager):
        """
        Initialize the dashboard.
        
        Args:
            data_manager: Data manager instance for retrieving data
        """
        self.data_manager = data_manager
        self.app = dash.Dash(__name__, 
                            title="Schwab API Dashboard",
                            meta_tags=[{"name": "viewport", 
                                       "content": "width=device-width, initial-scale=1"}])
        self.server = self.app.server
        self.default_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        self.current_symbols = self.default_symbols.copy()
        
        # Initialize real-time integration
        self.realtime = RealTimeIntegration(data_manager)
        self.realtime_active = False
        
        # Initialize real-time handler
        from .realtime_handler import RealTimeHandler
        self.realtime_handler = RealTimeHandler(self)
        
        # Initialize the dashboard layout
        self._create_layout()
        
        # Set up callbacks
        self._setup_callbacks()
        
    def _create_layout(self):
        """
        Create the dashboard layout.
        """
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("Schwab API Dashboard", className="header-title"),
                html.P("Real-time and historical stock and options data", className="header-description")
            ], className="header"),
            
            # Main content
            html.Div([
                # Left panel - Controls
                html.Div([
                    html.Div([
                        html.H3("Data Controls", className="control-title"),
                        
                        # Symbol input
                        html.Label("Symbol:"),
                        dcc.Input(id="symbol-input", type="text", value="AAPL", className="control-input"),
                        html.Button("Add Symbol", id="add-symbol-button", className="control-button"),
                        
                        # Symbol list
                        html.Label("Tracked Symbols:"),
                        html.Div(id="symbol-list", className="symbol-list"),
                        
                        # Time period selector
                        html.Label("Time Period:"),
                        dcc.Dropdown(
                            id="time-period-dropdown",
                            options=[
                                {"label": "1 Day", "value": "day_1"},
                                {"label": "5 Days", "value": "day_5"},
                                {"label": "1 Month", "value": "month_1"},
                                {"label": "3 Months", "value": "month_3"},
                                {"label": "1 Year", "value": "year_1"},
                                {"label": "5 Years", "value": "year_5"}
                            ],
                            value="day_1",
                            className="control-dropdown"
                        ),
                        
                        # Data type selector
                        html.Label("Data Type:"),
                        dcc.Dropdown(
                            id="data-type-dropdown",
                            options=[
                                {"label": "Price", "value": "price"},
                                {"label": "Volume", "value": "volume"},
                                {"label": "Options Chain", "value": "options"}
                            ],
                            value="price",
                            className="control-dropdown"
                        ),
                        
                        # Refresh button
                        html.Button("Refresh Data", id="refresh-button", className="control-button"),
                        
                        # Real-time toggle
                        html.Label("Real-time Updates:"),
                        dcc.RadioItems(
                            id="realtime-toggle",
                            options=[
                                {"label": "On", "value": "on"},
                                {"label": "Off", "value": "off"}
                            ],
                            value="off",
                            className="control-radio"
                        ),
                        
                        # Status indicator
                        html.Div([
                            html.Label("Status:"),
                            html.Div(id="status-indicator", className="status-indicator")
                        ], className="status-container")
                    ], className="control-panel-inner")
                ], className="control-panel"),
                
                # Right panel - Visualizations
                html.Div([
                    # Tabs for different visualizations
                    dcc.Tabs([
                        # Price Chart Tab
                        dcc.Tab(label="Price Chart", children=[
                            dcc.Graph(id="price-chart", className="chart")
                        ]),
                        
                        # Volume Chart Tab
                        dcc.Tab(label="Volume Chart", children=[
                            dcc.Graph(id="volume-chart", className="chart")
                        ]),
                        
                        # Options Chain Tab
                        dcc.Tab(label="Options Chain", children=[
                            html.Div([
                                # Options controls
                                html.Div([
                                    html.Label("Expiration Date:"),
                                    dcc.Dropdown(id="expiration-dropdown", className="options-dropdown"),
                                    
                                    html.Label("Option Type:"),
                                    dcc.RadioItems(
                                        id="option-type-radio",
                                        options=[
                                            {"label": "Calls", "value": "calls"},
                                            {"label": "Puts", "value": "puts"},
                                            {"label": "Both", "value": "both"}
                                        ],
                                        value="both",
                                        className="options-radio"
                                    )
                                ], className="options-controls"),
                                
                                # Options table
                                html.Div(id="options-table", className="options-table")
                            ], className="options-container")
                        ]),
                        
                        # Data Table Tab
                        dcc.Tab(label="Data Table", children=[
                            html.Div(id="data-table", className="data-table")
                        ])
                    ], id="tabs", className="tabs")
                ], className="visualization-panel")
            ], className="main-content"),
            
            # Hidden divs for storing data
            html.Div(id="stored-data", style={"display": "none"}),
            html.Div(id="options-data", style={"display": "none"}),
            
            # Interval component for automatic updates
            dcc.Interval(
                id="update-interval",
                interval=5*1000,  # 5 seconds in milliseconds
                n_intervals=0,
                disabled=True
            )
        ], className="dashboard-container")
    
    def _setup_callbacks(self):
        """
        Set up the dashboard callbacks.
        """
        # Callback to update symbol list
        @self.app.callback(
            Output("symbol-list", "children"),
            [Input("add-symbol-button", "n_clicks")],
            [State("symbol-input", "value"),
             State("symbol-list", "children")]
        )
        def update_symbol_list(n_clicks, symbol, current_list):
            if n_clicks is None:
                # Initialize with default symbols
                return [html.Div([
                    html.Span(s),
                    html.Button("×", id={"type": "remove-symbol", "index": i}, className="remove-button")
                ], className="symbol-item") for i, s in enumerate(self.current_symbols)]
            
            if symbol and symbol.upper() not in self.current_symbols:
                self.current_symbols.append(symbol.upper())
            
            return [html.Div([
                html.Span(s),
                html.Button("×", id={"type": "remove-symbol", "index": i}, className="remove-button")
            ], className="symbol-item") for i, s in enumerate(self.current_symbols)]
        
        # Callback to remove symbols
        @self.app.callback(
            Output("symbol-list", "children", allow_duplicate=True),
            [Input({"type": "remove-symbol", "index": dash.ALL}, "n_clicks")],
            [State("symbol-list", "children")],
            prevent_initial_call=True
        )
        def remove_symbol(n_clicks, current_list):
            ctx = dash.callback_context
            if not ctx.triggered:
                return current_list
            
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            index = eval(button_id)["index"]
            
            if index < len(self.current_symbols):
                self.current_symbols.pop(index)
            
            return [html.Div([
                html.Span(s),
                html.Button("×", id={"type": "remove-symbol", "index": i}, className="remove-button")
            ], className="symbol-item") for i, s in enumerate(self.current_symbols)]
        
        # Callback to fetch and store data
        @self.app.callback(
            [Output("stored-data", "children"),
             Output("status-indicator", "children")],
            [Input("refresh-button", "n_clicks"),
             Input("update-interval", "n_intervals")],
            [State("time-period-dropdown", "value")]
        )
        def fetch_and_store_data(n_clicks, n_intervals, time_period):
            # Initialize with empty data
            if n_clicks is None and n_intervals == 0:
                return "", html.Span("Idle", className="status-idle")
            
            try:
                # Parse time period
                period_type, period = self._parse_time_period(time_period)
                
                # Determine appropriate frequency based on period
                frequency_type, frequency = self._determine_frequency(period_type, period)
                
                # Fetch data for each symbol
                all_data = {}
                for symbol in self.current_symbols:
                    df = self.data_manager.get_price_history(
                        symbol=symbol,
                        period_type=period_type,
                        period=period,
                        frequency_type=frequency_type,
                        frequency=frequency
                    )
                    
                    if not df.empty:
                        all_data[symbol] = df.to_json(date_format='iso', orient='split')
                
                # Store data as JSON string
                return str(all_data), html.Span("Data Updated", className="status-success")
            
            except Exception as e:
                logger.error(f"Error fetching data: {str(e)}")
                return "", html.Span(f"Error: {str(e)}", className="status-error")
        
        # Callback to update price chart
        @self.app.callback(
            Output("price-chart", "figure"),
            [Input("stored-data", "children"),
             Input("update-interval", "n_intervals")]
        )
        def update_price_chart(stored_data, n_intervals):
            # Check if real-time is active
            if self.realtime_active and n_intervals > 0:
                # Use real-time data
                return self.realtime_handler.get_real_time_price_figure(self.current_symbols)
            
            if not stored_data:
                # Return empty figure
                return {
                    "data": [],
                    "layout": {
                        "title": "Price Chart",
                        "xaxis": {"title": "Date"},
                        "yaxis": {"title": "Price ($)"}
                    }
                }
            
            try:
                # Parse stored data
                all_data = eval(stored_data)
                
                # Create traces for each symbol
                traces = []
                for symbol, json_data in all_data.items():
                    df = pd.read_json(json_data, orient='split')
                    
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
                        "title": "Price Chart",
                        "xaxis": {"title": "Date"},
                        "yaxis": {"title": "Price ($)"},
                        "hovermode": "closest"
                    }
                }
                
                return figure
            
            except Exception as e:
                logger.error(f"Error updating price chart: {str(e)}")
                return {
                    "data": [],
                    "layout": {
                        "title": f"Error: {str(e)}",
                        "xaxis": {"title": "Date"},
                        "yaxis": {"title": "Price ($)"}
                    }
                }
        
        # Callback to update volume chart
        @self.app.callback(
            Output("volume-chart", "figure"),
            [Input("stored-data", "children"),
             Input("update-interval", "n_intervals")]
        )
        def update_volume_chart(stored_data, n_intervals):
            # Check if real-time is active
            if self.realtime_active and n_intervals > 0:
                # Use real-time data
                return self.realtime_handler.get_real_time_volume_figure(self.current_symbols)
            
            if not stored_data:
                # Return empty figure
                return {
                    "data": [],
                    "layout": {
                        "title": "Volume Chart",
                        "xaxis": {"title": "Date"},
                        "yaxis": {"title": "Volume"}
                    }
                }
            
            try:
                # Parse stored data
                all_data = eval(stored_data)
                
                # Create traces for each symbol
                traces = []
                for symbol, json_data in all_data.items():
                    df = pd.read_json(json_data, orient='split')
                    
                    traces.append(go.Bar(
                        x=df['datetime'],
                        y=df['volume'],
                        name=symbol
                    ))
                
                # Create figure
                figure = {
                    "data": traces,
                    "layout": {
                        "title": "Volume Chart",
                        "xaxis": {"title": "Date"},
                        "yaxis": {"title": "Volume"},
                        "barmode": "group"
                    }
                }
                
                return figure
            
            except Exception as e:
                logger.error(f"Error updating volume chart: {str(e)}")
                return {
                    "data": [],
                    "layout": {
                        "title": f"Error: {str(e)}",
                        "xaxis": {"title": "Date"},
                        "yaxis": {"title": "Volume"}
                    }
                }
        
        # Callback to update options table
        @self.app.callback(
            Output("options-table", "children"),
            [Input("symbol-input", "value"),
             Input("option-type-radio", "value"),
             Input("update-interval", "n_intervals")]
        )
        def update_options_table(symbol, option_type, n_intervals):
            # Check if real-time is active
            if self.realtime_active and n_intervals > 0 and symbol:
                # Use real-time data
                return self.realtime_handler.get_real_time_option_table(symbol, option_type)
            
            # If not real-time or no symbol, try to get historical data
            if not symbol:
                return html.Div("Enter a symbol to view options data")
            
            try:
                # Get option chain from data manager
                option_chain = self.data_manager.get_option_chain(symbol)
                
                # Format option chain for display
                return format_option_chain_table(option_chain, option_type)
            except Exception as e:
                logger.error(f"Error updating options table: {str(e)}")
                return html.Div(f"Error: {str(e)}")
        
        # Callback to toggle real-time updates
        @self.app.callback(
            [Output("update-interval", "disabled"),
             Output("status-indicator", "children")],
            [Input("realtime-toggle", "value")]
        )
        def toggle_realtime(value):
            if value == "on" and not self.realtime_active:
                # Start real-time streaming
                success = self.realtime.start_streaming(symbols=self.current_symbols)
                self.realtime_active = success
                
                if success:
                    return False, html.Span("Real-time streaming active", className="status-success")
                else:
                    return True, html.Span("Failed to start real-time streaming", className="status-error")
            elif value == "off" and self.realtime_active:
                # Stop real-time streaming
                success = self.realtime.stop_streaming()
                self.realtime_active = not success
                
                if success:
                    return True, html.Span("Real-time streaming stopped", className="status-idle")
                else:
                    return False, html.Span("Failed to stop real-time streaming", className="status-error")
            
            return value != "on", html.Span("Idle", className="status-idle")
    
    def _parse_time_period(self, time_period):
        """
        Parse time period string into period type and period.
        
        Args:
            time_period (str): Time period string (e.g., 'day_1', 'month_3', 'year_5')
            
        Returns:
            tuple: (period_type, period)
        """
        parts = time_period.split('_')
        period_type = parts[0]
        period = int(parts[1])
        
        return period_type, period
    
    def _determine_frequency(self, period_type, period):
        """
        Determine appropriate frequency based on period type and period.
        
        Args:
            period_type (str): Period type ('day', 'month', 'year')
            period (int): Period value
            
        Returns:
            tuple: (frequency_type, frequency)
        """
        if period_type == 'day':
            if period <= 1:
                return 'minute', 5
            else:
                return 'minute', 30
        elif period_type == 'month':
            if period <= 1:
                return 'daily', 1
            else:
                return 'daily', 1
        elif period_type == 'year':
            if period <= 1:
                return 'weekly', 1
            else:
                return 'monthly', 1
        else:
            return 'daily', 1
    
    def run(self, debug=False, port=8050):
        """
        Run the dashboard server.
        
        Args:
            debug (bool): Whether to run in debug mode
            port (int): Port to run the server on
        """
        self.app.run(debug=debug, port=port, host='0.0.0.0')
