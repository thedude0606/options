# Schwab API Dashboard

A dashboard application for viewing stock and options data using Schwab APIs.

## Features

- **Authentication**: Secure OAuth authentication with Schwab API
- **Historical Data**: Retrieve and visualize historical stock price data
- **Options Data**: View and analyze options chains with greeks
- **Real-time Updates**: Stream real-time quotes and option data
- **Interactive Dashboard**: User-friendly interface for data visualization

## Requirements

- Python 3.11 or higher
- Schwab developer account with API credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/thedude0606/options.git
cd options
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root with the following:
```
SCHWAB_APP_KEY=your_app_key
SCHWAB_APP_SECRET=your_app_secret
SCHWAB_CALLBACK_URL=your_callback_url
```

## Usage

1. Run the main application:
```bash
python main.py
```

2. Navigate to `http://localhost:8050` in your web browser to access the dashboard.

3. Authenticate with your Schwab account when prompted.

4. Use the dashboard to view and analyze stock and options data.

## Project Structure

- `src/auth/`: Authentication components
- `src/data/`: Data retrieval and processing
- `src/dashboard/`: Dashboard interface and visualization
- `test_app.py`: Application tests
- `test_app_mock.py`: Mock tests for CI/CD environments
- `test_dashboard.py`: Dashboard component tests

## Documentation

- `PROGRESS.md`: Development progress and status
- `TODO.md`: Task list and priorities
- `DECISIONS.md`: Design decisions and rationale

## License

This project is licensed under the MIT License - see the LICENSE file for details.
