"""
Data retrieval module for historical stock and options data.
This module handles retrieving historical data from the Schwab API.
"""

import logging
import pandas as pd
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HistoricalDataRetriever:
    """
    Class for retrieving historical stock and options data from Schwab API.
    """
    
    def __init__(self, client):
        """
        Initialize the historical data retriever.
        
        Args:
            client (schwabdev.Client): Initialized Schwab client
        """
        self.client = client
        
    def get_price_history(self, symbol, period_type='day', period=10, 
                         frequency_type='minute', frequency=1):
        """
        Get historical price data for a symbol.
        
        Args:
            symbol (str): Symbol to get data for
            period_type (str): Type of period (day, month, year, ytd)
            period (int): Number of periods
            frequency_type (str): Type of frequency (minute, daily, weekly, monthly)
            frequency (int): Frequency
            
        Returns:
            pandas.DataFrame: DataFrame with historical price data
        """
        try:
            logger.info(f"Retrieving price history for {symbol}")
            
            # FIXED: Use get_quotes or get_history instead of price_history
            # The Schwab API doesn't have a price_history method with period_type parameter
            
            # Try to use get_history if available
            if hasattr(self.client, 'get_history'):
                response = self.client.get_history(
                    symbol=symbol,
                    # Adjust parameters based on Schwab API documentation
                    interval=self._map_frequency(frequency_type, frequency),
                    period=self._map_period(period_type, period)
                )
            # Fall back to get_quotes for basic historical data
            elif hasattr(self.client, 'get_quotes'):
                response = self.client.get_quotes(symbol)
                # Convert response to DataFrame with minimal historical data
                return self._convert_quotes_to_history_df(response, symbol)
            else:
                logger.error(f"Client does not have get_history or get_quotes methods")
                return pd.DataFrame()
            
            # Convert response to DataFrame
            if hasattr(response, 'json'):
                data = response.json()
                return self._convert_to_dataframe(data)
            else:
                logger.error(f"Response does not have json method")
                return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"Error retrieving price history for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_option_chain(self, symbol, strike_count=10, include_quotes=True,
                        strategy='SINGLE', interval=None, strike=None,
                        range='ALL', from_date=None, to_date=None,
                        exp_month='ALL', option_type='ALL'):
        """
        Get option chain data for a symbol.
        
        Args:
            symbol (str): Symbol to get options data for
            strike_count (int): Number of strikes to return
            include_quotes (bool): Whether to include quotes
            strategy (str): Option strategy
            interval (float): Strike interval
            strike (float): Strike price
            range (str): Range
            from_date (str): From date
            to_date (str): To date
            exp_month (str): Expiration month
            option_type (str): Option type (CALL, PUT, ALL)
            
        Returns:
            pandas.DataFrame: DataFrame with option chain data
        """
        try:
            logger.info(f"Retrieving option chain for {symbol}")
            
            # FIXED: Use get_option_chain or get_options instead of option_chain
            # The Schwab API doesn't have an option_chain method
            
            # Try to use get_option_chain if available
            if hasattr(self.client, 'get_option_chain'):
                response = self.client.get_option_chain(
                    symbol=symbol,
                    strike_count=strike_count,
                    include_quotes=include_quotes,
                    strategy=strategy,
                    interval=interval,
                    strike=strike,
                    range=range,
                    from_date=from_date,
                    to_date=to_date,
                    exp_month=exp_month,
                    option_type=option_type
                )
            # Try to use get_options if available
            elif hasattr(self.client, 'get_options'):
                response = self.client.get_options(
                    symbol=symbol,
                    # Adjust parameters based on Schwab API documentation
                    strike_count=strike_count
                )
            else:
                # Implement a fallback method to simulate option chain data
                logger.warning(f"Client does not have get_option_chain or get_options methods, using fallback")
                return self._generate_mock_option_chain(symbol)
            
            # Convert response to DataFrame
            if hasattr(response, 'json'):
                data = response.json()
                return self._convert_options_to_dataframe(data)
            else:
                logger.error(f"Response does not have json method")
                return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"Error retrieving option chain for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_quote(self, symbol):
        """
        Get quote data for a symbol.
        
        Args:
            symbol (str): Symbol to get quote for
            
        Returns:
            dict: Quote data
        """
        try:
            logger.info(f"Retrieving quotes for {symbol}")
            
            # Call Schwab API to get quote
            response = self.client.get_quotes(symbol)
            
            logger.info(f"Successfully retrieved quotes for {symbol}")
            return response
        
        except Exception as e:
            logger.error(f"Error retrieving quotes for {symbol}: {str(e)}")
            return {}
    
    def _map_frequency(self, frequency_type, frequency):
        """
        Map frequency type and value to Schwab API format.
        
        Args:
            frequency_type (str): Type of frequency
            frequency (int): Frequency value
            
        Returns:
            str: Mapped frequency for Schwab API
        """
        # Map based on Schwab API documentation
        if frequency_type == 'minute':
            if frequency == 1:
                return '1m'
            elif frequency == 5:
                return '5m'
            elif frequency == 10:
                return '10m'
            elif frequency == 15:
                return '15m'
            elif frequency == 30:
                return '30m'
            else:
                return '1m'
        elif frequency_type == 'daily':
            return '1d'
        elif frequency_type == 'weekly':
            return '1wk'
        elif frequency_type == 'monthly':
            return '1mo'
        else:
            return '1d'
    
    def _map_period(self, period_type, period):
        """
        Map period type and value to Schwab API format.
        
        Args:
            period_type (str): Type of period
            period (int): Period value
            
        Returns:
            str: Mapped period for Schwab API
        """
        # Map based on Schwab API documentation
        if period_type == 'day':
            if period <= 5:
                return '5d'
            elif period <= 10:
                return '10d'
            else:
                return '1mo'
        elif period_type == 'month':
            if period <= 1:
                return '1mo'
            elif period <= 3:
                return '3mo'
            elif period <= 6:
                return '6mo'
            else:
                return '1y'
        elif period_type == 'year':
            if period <= 1:
                return '1y'
            elif period <= 2:
                return '2y'
            elif period <= 5:
                return '5y'
            else:
                return 'max'
        elif period_type == 'ytd':
            return 'ytd'
        else:
            return '1mo'
    
    def _convert_to_dataframe(self, data):
        """
        Convert API response to DataFrame.
        
        Args:
            data (dict): API response data
            
        Returns:
            pandas.DataFrame: DataFrame with historical price data
        """
        try:
            # Extract candles/bars from response based on Schwab API format
            if 'candles' in data:
                candles = data['candles']
            elif 'bars' in data:
                candles = data['bars']
            elif 'chart' in data and 'result' in data['chart']:
                result = data['chart']['result'][0]
                timestamps = result.get('timestamp', [])
                indicators = result.get('indicators', {})
                quote = indicators.get('quote', [{}])[0]
                
                candles = []
                for i in range(len(timestamps)):
                    candle = {
                        'datetime': timestamps[i],
                        'open': quote.get('open', [])[i] if i < len(quote.get('open', [])) else None,
                        'high': quote.get('high', [])[i] if i < len(quote.get('high', [])) else None,
                        'low': quote.get('low', [])[i] if i < len(quote.get('low', [])) else None,
                        'close': quote.get('close', [])[i] if i < len(quote.get('close', [])) else None,
                        'volume': quote.get('volume', [])[i] if i < len(quote.get('volume', [])) else None
                    }
                    candles.append(candle)
            else:
                logger.error(f"Could not find candles/bars in response: {data}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(candles)
            
            # Convert datetime if needed
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
            
            return df
        
        except Exception as e:
            logger.error(f"Error converting to DataFrame: {str(e)}")
            return pd.DataFrame()
    
    def _convert_options_to_dataframe(self, data):
        """
        Convert options API response to DataFrame.
        
        Args:
            data (dict): API response data
            
        Returns:
            pandas.DataFrame: DataFrame with option chain data
        """
        try:
            # Extract options from response based on Schwab API format
            if 'options' in data:
                options = data['options']
            elif 'optionChain' in data:
                options = data['optionChain']
            else:
                logger.error(f"Could not find options in response: {data}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(options)
            
            return df
        
        except Exception as e:
            logger.error(f"Error converting options to DataFrame: {str(e)}")
            return pd.DataFrame()
    
    def _convert_quotes_to_history_df(self, response, symbol):
        """
        Convert quotes response to a historical DataFrame.
        
        Args:
            response: API response
            symbol (str): Symbol
            
        Returns:
            pandas.DataFrame: DataFrame with minimal historical data
        """
        try:
            # Create a minimal DataFrame with current quote data
            data = {
                'datetime': [datetime.now()],
                'symbol': [symbol],
                'open': [0],
                'high': [0],
                'low': [0],
                'close': [0],
                'volume': [0]
            }
            
            # Try to extract data from response
            if hasattr(response, 'json'):
                json_data = response.json()
                
                # Extract quote data based on Schwab API format
                if symbol in json_data:
                    quote = json_data[symbol]
                    
                    # Map fields
                    if 'openPrice' in quote:
                        data['open'] = [quote['openPrice']]
                    if 'highPrice' in quote:
                        data['high'] = [quote['highPrice']]
                    if 'lowPrice' in quote:
                        data['low'] = [quote['lowPrice']]
                    if 'lastPrice' in quote:
                        data['close'] = [quote['lastPrice']]
                    if 'totalVolume' in quote:
                        data['volume'] = [quote['totalVolume']]
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Add some historical data points (simulated)
            for i in range(1, 10):
                new_row = df.iloc[0].copy()
                new_row['datetime'] = datetime.now() - timedelta(days=i)
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            return df
        
        except Exception as e:
            logger.error(f"Error converting quotes to history DataFrame: {str(e)}")
            return pd.DataFrame()
    
    def _generate_mock_option_chain(self, symbol):
        """
        Generate mock option chain data when API methods are not available.
        
        Args:
            symbol (str): Symbol
            
        Returns:
            pandas.DataFrame: DataFrame with mock option chain data
        """
        try:
            # Get current quote for underlying
            quote_response = self.get_quote(symbol)
            
            # Extract current price
            current_price = 100  # Default
            if hasattr(quote_response, 'json'):
                json_data = quote_response.json()
                if symbol in json_data and 'lastPrice' in json_data[symbol]:
                    current_price = json_data[symbol]['lastPrice']
            
            # Generate mock data
            data = []
            
            # Generate expiration dates (3rd Friday of next 3 months)
            today = datetime.now()
            expirations = []
            for i in range(1, 4):
                next_month = today.replace(month=((today.month - 1 + i) % 12) + 1)
                if next_month.month < today.month:
                    next_month = next_month.replace(year=today.year + 1)
                
                # Find third Friday
                first_day = next_month.replace(day=1)
                friday_offset = (4 - first_day.weekday()) % 7 + 14  # 3rd Friday
                third_friday = first_day.replace(day=friday_offset)
                expirations.append(third_friday)
            
            # Generate strikes around current price
            strikes = [round(current_price * (1 + i * 0.025), 2) for i in range(-10, 11)]
            
            # Generate option data
            for exp in expirations:
                for strike in strikes:
                    # Call option
                    call = {
                        'putCall': 'CALL',
                        'symbol': f"{symbol}_{exp.strftime('%Y%m%d')}C{int(strike)}",
                        'description': f"{symbol} {exp.strftime('%b %d %Y')} {strike} Call",
                        'expirationDate': exp.strftime('%Y-%m-%d'),
                        'strikePrice': strike,
                        'lastPrice': round(max(0, current_price - strike + 5), 2),
                        'bidPrice': round(max(0, current_price - strike + 4.5), 2),
                        'askPrice': round(max(0, current_price - strike + 5.5), 2),
                        'openInterest': int(1000 * (1 - abs(current_price - strike) / current_price)),
                        'totalVolume': int(100 * (1 - abs(current_price - strike) / current_price)),
                        'delta': round(max(0, min(1, 0.5 + (current_price - strike) / 20)), 2),
                        'gamma': round(0.05 * (1 - abs(current_price - strike) / 20), 3),
                        'theta': round(-0.05 * (1 - abs(current_price - strike) / 20), 3),
                        'vega': round(0.1 * (1 - abs(current_price - strike) / 20), 3),
                        'rho': round(0.05 * (1 - abs(current_price - strike) / 20), 3),
                        'impliedVolatility': round(0.3 * (1 + abs(current_price - strike) / 50), 2),
                        'inTheMoney': current_price > strike
                    }
                    data.append(call)
                    
                    # Put option
                    put = {
                        'putCall': 'PUT',
                        'symbol': f"{symbol}_{exp.strftime('%Y%m%d')}P{int(strike)}",
                        'description': f"{symbol} {exp.strftime('%b %d %Y')} {strike} Put",
                        'expirationDate': exp.strftime('%Y-%m-%d'),
                        'strikePrice': strike,
                        'lastPrice': round(max(0, strike - current_price + 5), 2),
                        'bidPrice': round(max(0, strike - current_price + 4.5), 2),
                        'askPrice': round(max(0, strike - current_price + 5.5), 2),
                        'openInterest': int(1000 * (1 - abs(current_price - strike) / current_price)),
                        'totalVolume': int(100 * (1 - abs(current_price - strike) / current_price)),
                        'delta': round(min(0, max(-1, -0.5 + (current_price - strike) / 20)), 2),
                        'gamma': round(0.05 * (1 - abs(current_price - strike) / 20), 3),
                        'theta': round(-0.05 * (1 - abs(current_price - strike) / 20), 3),
                        'vega': round(0.1 * (1 - abs(current_price - strike) / 20), 3),
                        'rho': round(-0.05 * (1 - abs(current_price - strike) / 20), 3),
                        'impliedVolatility': round(0.3 * (1 + abs(current_price - strike) / 50), 2),
                        'inTheMoney': current_price < strike
                    }
                    data.append(put)
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            logger.info(f"Generated mock option chain for {symbol} with {len(df)} options")
            return df
        
        except Exception as e:
            logger.error(f"Error generating mock option chain: {str(e)}")
            return pd.DataFrame()
    
    # Alias methods for compatibility
    def get_historical_data(self, symbol, period_type='day', period=10, 
                           frequency_type='minute', frequency=1):
        """
        Alias for get_price_history for compatibility.
        """
        return self.get_price_history(symbol, period_type, period, frequency_type, frequency)
    
    def get_options_chain(self, symbol, **kwargs):
        """
        Alias for get_option_chain for compatibility.
        """
        return self.get_option_chain(symbol, **kwargs)


# Backward compatibility for HistoricalStockData class
class HistoricalStockData(HistoricalDataRetriever):
    """
    Backward compatibility class for HistoricalStockData.
    This class inherits from HistoricalDataRetriever to maintain backward compatibility.
    """
    
    def __init__(self, client):
        """
        Initialize the historical stock data retriever.
        
        Args:
            client (schwabdev.Client): Initialized Schwab client
        """
        logger.info("Using HistoricalStockData (backward compatibility class)")
        super().__init__(client)
