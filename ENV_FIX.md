# Environment File Fix

If you're seeing errors like `Python-dotenv could not parse statement starting at line X`, your `.env` file is likely malformed.

## How to Fix Your .env File

Your `.env` file should be formatted with simple KEY=VALUE pairs without quotes or spaces around the equals sign.

### Correct Format:
```
SCHWAB_APP_KEY=your_app_key
SCHWAB_APP_SECRET=your_app_secret
SCHWAB_CALLBACK_URL=your_callback_url
```

### Common Issues to Avoid:
- No spaces around the equals sign
- No quotes around values
- No comments in the file
- No trailing spaces
- Make sure each entry is on its own line
- No empty lines between entries

## Additional Debugging Steps

If you're still not seeing data in the dashboard after fixing your `.env` file:

1. **Enable Debug Logging**: Add this code to your main.py before starting the dashboard:
   ```python
   # Enable debug logging
   logging.getLogger('src.data.realtime').setLevel(logging.DEBUG)
   logging.getLogger('src.dashboard.realtime_integration').setLevel(logging.DEBUG)
   logging.getLogger('src.dashboard.realtime_handler').setLevel(logging.DEBUG)
   ```

2. **Test Data Retrieval**: Add this code to test basic data retrieval:
   ```python
   # Get a quote for a test symbol
   test_symbol = 'AAPL'
   logger.info(f"Testing data retrieval with symbol: {test_symbol}")
   quote = data_manager.get_quote(test_symbol)
   logger.info(f"Quote data: {quote}")
   ```

3. **Manually Start Streaming**: Try explicitly starting the streaming:
   ```python
   # Try to start streaming explicitly
   logger.info("Attempting to start real-time streaming manually")
   streaming_result = data_manager.start_streaming(
       symbols=['AAPL', 'MSFT'], 
       handlers={'QUOTE': lambda x: logger.info(f"QUOTE update: {x}")}
   )
   logger.info(f"Streaming start result: {streaming_result}")
   ```

4. **Check Dashboard UI Settings**:
   - Make sure you've toggled the "Real-time Updates" to "On" in the dashboard UI
   - Add a symbol like "AAPL" using the "Add Symbol" button
   - Try different time periods in the dropdown

5. **Verify API Permissions**:
   - Ensure your Schwab API credentials have permissions for real-time data
   - Check if your account type supports the data you're requesting
