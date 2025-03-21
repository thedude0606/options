"""
Dashboard module for visualizing stock and options data.
This module provides the main dashboard interface for the application.
"""

import logging
import dash
from dash import dcc, html, callback, Input, Output, State, callback_context
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
            [State("symbol-list", "children")]
        )
        def remove_symbol(n_clicks_list, current_list):
            # Find which button was clicked
            ctx = callback_context
            if not ctx.triggered:
                return dash.no_update
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if not button_id:
                return dash.no_update
            
            try:
                # Extract the index from the button ID
                import json
                button_data = json.loads(button_id)
                index = button_data['index']
                
                # Remove the symbol from the list
                if index < len(self.current_symbols):
                    del self.current_symbols[index]
                
                # Return the updated list
                return [html.Div([
                    html.Span(s),
                    html.Button("×", id={"type": "remove-symbol", "index": i}, className="remove-button")
                ], className="symbol-item") for i, s in enumerate(self.current_symbols)]
            except Exception as e:
                logger.error(f"Error removing symbol: {str(e)}")
                return dash.no_update
        
        # Callback to fetch and store data
        @self.app.callback(
            [Output("stored-data", "children"),
             Output("status-indicator", "children", allow_duplicate=True)],
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
                
                # Check which input triggered the callback
                ctx = callback_context
                trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
                
                # Fetch data for each symbol
                all_data = {}
                for symbol in self.current_symbols:
                    try:
                        # Get historical data
                        data = self.data_manager.get_historical_data(
                            symbol=symbol,
                            period_type=period_type,
                            period=period
                        )
                        
                        if data is not None:
                            all_data[symbol] = data
                    except Exception as e:
                        logger.error(f"Error fetching data for {symbol}: {str(e)}")
                
                # Store data as JSON
                import json
                stored_data = json.dumps(all_data)
                
                # Update status
                if trigger_id == "refresh-button":
                    status = html.Span("Data refreshed", className="status-success")
                else:
                    status = html.Span("Data updated", className="status-success")
                
                return stored_data, status
            except Exception as e:
                logger.error(f"Error fetching and storing data: {str(e)}")
                return "", html.Span(f"Error: {str(e)}", className="status-error")
        
        # Callback to update price chart
        @self.app.callback(
            Output("price-chart", "figure"),
            [Input("stored-data", "children"),
             Input("tabs", "value")],
            [State("time-period-dropdown", "value")]
        )
        def update_price_chart(stored_data, tab_value, time_period):
            if not stored_data:
                return {
                    "data": [],
                    "layout": {
                        "title": "Price Chart (No Data Available)",
                        "xaxis": {"title": "Date"},
                        "yaxis": {"title": "Price ($)"}
                    }
                }
            
            try:
                # Parse stored data
                import json
                all_data = json.loads(stored_data)
                
                if not all_data:
                    return {
                        "data": [],
                        "layout": {
                            "title": "Price Chart (No Data Available)",
                            "xaxis": {"title": "Date"},
                            "yaxis": {"title": "Price ($)"}
                        }
                    }
                
                # Create candlestick chart
                return create_candlestick_chart(all_data, time_period)
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
             Input("tabs", "value")]
        )
        def update_volume_chart(stored_data, tab_value):
            if not stored_data:
                return {
                    "data": [],
                    "layout": {
                        "title": "Volume Chart (No Data Available)",
                        "xaxis": {"title": "Date"},
                        "yaxis": {"title": "Volume"}
                    }
                }
            
            try:
                # Parse stored data
                import json
                all_data = json.loads(stored_data)
                
                if not all_data:
                    return {
                        "data": [],
                        "layout": {
                            "title": "Volume Chart (No Data Available)",
                            "xaxis": {"title": "Date"},
                            "yaxis": {"title": "Volume"}
                        }
                    }
                
                # Create volume chart
                traces = []
                for symbol, data in all_data.items():
                    if not data:
                        continue
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(data)
                    
                    if df.empty:
                        continue
                    
                    # Add volume trace
                    traces.append(go.Bar(
                        x=df['datetime'],
                        y=df['volume'],
                        name=f"{symbol} Volume"
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
        
        # Callback to update options data
        @self.app.callback(
            [Output("options-data", "children"),
             Output("expiration-dropdown", "options")],
            [Input("symbol-input", "value"),
             Input("tabs", "value")]
        )
        def update_options_data(symbol, tab_value):
            if not symbol:
                return "", []
            
            try:
                # Get options chain
                options_chain = self.data_manager.get_options_chain(symbol)
                
                if not options_chain:
                    return "", []
                
                # Store options data as JSON
                import json
                stored_data = json.dumps(options_chain)
                
                # Get expiration dates
                expiration_dates = get_expiration_dates(options_chain)
                
                # Create dropdown options
                dropdown_options = [{"label": date, "value": date} for date in expiration_dates]
                
                return stored_data, dropdown_options
            except Exception as e:
                logger.error(f"Error updating options data: {str(e)}")
                return "", []
        
        # Callback to update options table
        @self.app.callback(
            Output("options-table", "children"),
            [Input("options-data", "children"),
             Input("expiration-dropdown", "value"),
             Input("option-type-radio", "value")]
        )
        def update_options_table(options_data, expiration_date, option_type):
            if not options_data or not expiration_date:
                return html.Div("Select a symbol and expiration date to view options chain")
            
            try:
                # Parse options data
                import json
                option_chain = json.loads(options_data)
                
                # Format option chain for display
                return format_option_chain_table(option_chain, option_type)
            except Exception as e:
                logger.error(f"Error updating options table: {str(e)}")
                return html.Div(f"Error: {str(e)}")
        
        # Callback to toggle real-time updates
        @self.app.callback(
            [Output("update-interval", "disabled"),
             Output("status-indicator", "children", allow_duplicate=True)],
            [Input("realtime-toggle", "value")]
        )
        def toggle_realtime(value):
            # Check which input triggered the callback
            ctx = callback_context
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
            
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
            else:
                # No change
                return True if value == "off" else False, dash.no_update
        
        # Callback to update data table
        @self.app.callback(
            Output("data-table", "children"),
            [Input("stored-data", "children"),
             Input("tabs", "value")]
        )
        def update_data_table(stored_data, tab_value):
            if not stored_data:
                return html.Div("No data available")
            
            try:
                # Parse stored data
                import json
                all_data = json.loads(stored_data)
                
                if not all_data:
                    return html.Div("No data available")
                
                # Create data table
                return create_data_table(all_data)
            except Exception as e:
                logger.error(f"Error updating data table: {str(e)}")
                return html.Div(f"Error: {str(e)}")
    
    def _parse_time_period(self, time_period):
        """
        Parse time period string into period type and period.
        
        Args:
            time_period (str): Time period string (e.g., 'day_1', 'month_3')
            
        Returns:
            tuple: (period_type, period)
        """
        parts = time_period.split('_')
        if len(parts) != 2:
            return 'day', 1
        
        period_type = parts[0]
        try:
            period = int(parts[1])
        except ValueError:
            period = 1
        
        return period_type, period
    
    def run(self, host='0.0.0.0', port=8050, debug=True):
        """
        Run the dashboard server.
        
        Args:
            host (str): Host to run the server on
            port (int): Port to run the server on
            debug (bool): Whether to run in debug mode
        """
        logger.info(f"Starting dashboard server on port {port}")
        self.app.run_server(host=host, port=port, debug=debug)
