"""
Utility functions for the dashboard.
This module provides helper functions for data processing and visualization.
"""

import pandas as pd
import plotly.graph_objs as go
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def format_option_chain_table(option_chain, option_type='both'):
    """
    Format option chain data for display in a table.
    
    Args:
        option_chain (dict): Option chain data from Schwab API
        option_type (str): Type of options to include ('calls', 'puts', 'both')
        
    Returns:
        html.Table: Formatted table for display
    """
    from dash import html
    
    if not option_chain or 'callExpDateMap' not in option_chain or 'putExpDateMap' not in option_chain:
        return html.Div("No option data available")
    
    # Extract calls and puts
    calls = option_chain['callExpDateMap']
    puts = option_chain['putExpDateMap']
    
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
        html.Th("Vega")
    ]))
    
    # Create table rows
    rows = []
    
    # Process calls if requested
    if option_type in ['calls', 'both']:
        for exp_date, strikes in calls.items():
            for strike, options in strikes.items():
                for option in options:
                    rows.append(html.Tr([
                        html.Td(strike),
                        html.Td(exp_date.split(':')[0]),
                        html.Td("CALL"),
                        html.Td(option.get('symbol', '')),
                        html.Td(f"${option.get('bid', 0):.2f}"),
                        html.Td(f"${option.get('ask', 0):.2f}"),
                        html.Td(f"${option.get('last', 0):.2f}"),
                        html.Td(option.get('totalVolume', 0)),
                        html.Td(option.get('openInterest', 0)),
                        html.Td(f"{option.get('delta', 0):.3f}"),
                        html.Td(f"{option.get('gamma', 0):.3f}"),
                        html.Td(f"{option.get('theta', 0):.3f}"),
                        html.Td(f"{option.get('vega', 0):.3f}")
                    ]))
    
    # Process puts if requested
    if option_type in ['puts', 'both']:
        for exp_date, strikes in puts.items():
            for strike, options in strikes.items():
                for option in options:
                    rows.append(html.Tr([
                        html.Td(strike),
                        html.Td(exp_date.split(':')[0]),
                        html.Td("PUT"),
                        html.Td(option.get('symbol', '')),
                        html.Td(f"${option.get('bid', 0):.2f}"),
                        html.Td(f"${option.get('ask', 0):.2f}"),
                        html.Td(f"${option.get('last', 0):.2f}"),
                        html.Td(option.get('totalVolume', 0)),
                        html.Td(option.get('openInterest', 0)),
                        html.Td(f"{option.get('delta', 0):.3f}"),
                        html.Td(f"{option.get('gamma', 0):.3f}"),
                        html.Td(f"{option.get('theta', 0):.3f}"),
                        html.Td(f"{option.get('vega', 0):.3f}")
                    ]))
    
    # Create table body
    body = html.Tbody(rows)
    
    # Create table
    table = html.Table([header, body], className="option-table")
    
    return table

def create_candlestick_chart(df, title="Price Chart"):
    """
    Create a candlestick chart from price data.
    
    Args:
        df (pandas.DataFrame): Price data with OHLC columns
        title (str): Chart title
        
    Returns:
        dict: Plotly figure object
    """
    if df.empty:
        return {
            "data": [],
            "layout": {
                "title": title,
                "xaxis": {"title": "Date"},
                "yaxis": {"title": "Price ($)"}
            }
        }
    
    # Create candlestick trace
    candlestick = go.Candlestick(
        x=df['datetime'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="OHLC"
    )
    
    # Create figure
    figure = {
        "data": [candlestick],
        "layout": {
            "title": title,
            "xaxis": {"title": "Date"},
            "yaxis": {"title": "Price ($)"},
            "hovermode": "closest"
        }
    }
    
    return figure

def create_data_table(df, max_rows=50):
    """
    Create a data table from a DataFrame.
    
    Args:
        df (pandas.DataFrame): Data to display
        max_rows (int): Maximum number of rows to display
        
    Returns:
        html.Table: Formatted table for display
    """
    from dash import html
    
    if df.empty:
        return html.Div("No data available")
    
    # Limit rows
    if len(df) > max_rows:
        df = df.head(max_rows)
    
    # Create table header
    header = html.Thead(html.Tr([html.Th(col) for col in df.columns]))
    
    # Create table rows
    rows = []
    for i, row in df.iterrows():
        rows.append(html.Tr([html.Td(row[col]) for col in df.columns]))
    
    # Create table body
    body = html.Tbody(rows)
    
    # Create table
    table = html.Table([header, body], className="data-table")
    
    return table

def get_expiration_dates(option_chain):
    """
    Extract expiration dates from option chain data.
    
    Args:
        option_chain (dict): Option chain data from Schwab API
        
    Returns:
        list: List of expiration dates
    """
    if not option_chain or 'callExpDateMap' not in option_chain:
        return []
    
    # Extract expiration dates from calls
    exp_dates = list(option_chain['callExpDateMap'].keys())
    
    # Format dates for display
    formatted_dates = [date.split(':')[0] for date in exp_dates]
    
    return formatted_dates

def calculate_option_metrics(option_chain):
    """
    Calculate additional metrics for options analysis.
    
    Args:
        option_chain (dict): Option chain data from Schwab API
        
    Returns:
        dict: Dictionary with calculated metrics
    """
    if not option_chain or 'callExpDateMap' not in option_chain or 'putExpDateMap' not in option_chain:
        return {}
    
    metrics = {
        'call_volume_total': 0,
        'put_volume_total': 0,
        'call_open_interest_total': 0,
        'put_open_interest_total': 0,
        'put_call_ratio_volume': 0,
        'put_call_ratio_oi': 0
    }
    
    # Calculate call metrics
    for exp_date, strikes in option_chain['callExpDateMap'].items():
        for strike, options in strikes.items():
            for option in options:
                metrics['call_volume_total'] += option.get('totalVolume', 0)
                metrics['call_open_interest_total'] += option.get('openInterest', 0)
    
    # Calculate put metrics
    for exp_date, strikes in option_chain['putExpDateMap'].items():
        for strike, options in strikes.items():
            for option in options:
                metrics['put_volume_total'] += option.get('totalVolume', 0)
                metrics['put_open_interest_total'] += option.get('openInterest', 0)
    
    # Calculate ratios
    if metrics['call_volume_total'] > 0:
        metrics['put_call_ratio_volume'] = metrics['put_volume_total'] / metrics['call_volume_total']
    
    if metrics['call_open_interest_total'] > 0:
        metrics['put_call_ratio_oi'] = metrics['put_open_interest_total'] / metrics['call_open_interest_total']
    
    return metrics
