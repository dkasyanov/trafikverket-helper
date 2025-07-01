# Trafikverket Helper

[![Version](https://img.shields.io/github/v/release/ekvanox/trafikverket-helper)](https://img.shields.io/github/v/release/ekvanox/trafikverket-helper)
![GitHub repo size](https://img.shields.io/github/repo-size/ekvanox/trafikverket-helper)
[![CodeFactor](https://www.codefactor.io/repository/github/ekvanox/trafikverket-helper/badge)](https://www.codefactor.io/repository/github/ekvanox/trafikverket-helper)
![License](https://img.shields.io/github/license/ekvanox/trafikverket-helper)

This is a script for interacting with the Trafikverket API to retrieve information about available rides for driving examinations. It allows the user to select an examination type and execution mode, then retrieves available rides from the API and displays them in the console.

**New Feature**: The application now uses SQLite database for persistent storage, so your ride data is preserved between restarts!

**New Feature**: Automatic session management with cookie refresh capabilities!

![Usage example gif](https://github.com/ekvanox/trafikverket-helper/blob/master/images/usage.gif?raw=true)

## Requirements

- Python 3.7 or higher
- Valid Swedish Social Security Number (personnummer)
- Active Trafikverket account with login credentials

## Installation

Clone the repository and install the required packages:

```sh
$ git clone https://github.com/ekvanox/trafikverket-helper
$ cd trafikverket-helper
$ pip install -r requirements.txt
```

## Usage

To run the script, use the following command:

```sh
$ python main.py
```

## Modes

The script has three execution modes:

- **Monitor rides**: Continuously monitors ride availability and logs any changes, such as new or removed rides. Data is automatically persisted to the database.
- **Display rides**: View and manage ride data with options to display, filter, and clean stored ride information.
- **Start web server**: Starts a local web server to display the available rides in a web page.

## Session Management

The application now provides **automatic session management** with background cookie refresh:

- **Automatic cookie refresh**: Sessions are automatically refreshed 15 minutes before expiration
- **Background monitoring**: Continuous monitoring of session validity during long-running operations
- **Proactive renewal**: Automatic detection and renewal of expired sessions
- **Seamless operation**: No manual intervention required for session management

### How Automatic Session Management Works

1. **Initial cookies**: The application starts with cookies from `config.json`
2. **Background refresh**: Automatic refresh process runs every 5 minutes during monitoring mode
3. **Proactive detection**: The system detects when sessions are about to expire and refreshes them
4. **Error recovery**: If a session expires unexpectedly, the system attempts automatic recovery
5. **Persistent storage**: Updated cookies are maintained in memory and can be saved to config

### Initial Setup Requirements

Before running the application, you must have valid session cookies in your `config.json` file. The application cannot generate initial cookies - they must be obtained from an authenticated browser session with Trafikverket.

## Display Rides

The display rides mode provides several useful features:

- **View all rides**: Display all stored rides for the selected examination type
- **View rides by date range**: Filter rides between specific dates
- **View rides by location**: Show rides for a specific location
- **Clear old rides**: Remove rides older than a specified number of days
- **Show database statistics**: Display summary information about stored data

## Persistent Storage

The application now uses SQLite database (`data/rides.db`) to store ride information persistently. This means:

- **Data persistence**: Your ride data is preserved between application restarts
- **Faster startup**: The application can load cached data instead of fetching from the API every time
- **Historical data**: You can view and analyze ride data over time
- **Automatic cleanup**: Old rides can be automatically removed to keep the database size manageable

The database is automatically created in the `data/` directory when you first run the application.

## Configuration

The script uses a `config.json` file for settings and authentication. The file should be located in the same directory as the script, and should have the following format:

```json
{
  "swedish_ssn": "YYYYMMDD-XXXX",
  "cookies": {
    "FpsPartnerDeviceIdentifier": "your_device_identifier_here",
    "ASP.NET_SessionId": "your_session_id_here",
    "LoginValid": "2025-01-01 12:00",
    "FpsExternalIdentity": "your_external_identity_here"
  }
}
```

**Configuration Details:**
- `swedish_ssn`: Replace with your valid Swedish social security number (format: YYYYMMDD-XXXX)
- `cookies`: **Required** - Valid session cookies from an authenticated Trafikverket session

**Cookie Setup Instructions:**
1. Log into Trafikverket's booking system in your browser
2. Open browser developer tools (F12) and go to Network tab
3. Make a request to the booking system
4. Copy the cookies from the request headers
5. Add the cookies to your `config.json` file in the format shown above

**Required cookies include:**
- `FpsPartnerDeviceIdentifier`
- `ASP.NET_SessionId`
- `LoginValid`
- `FpsExternalIdentity`

**Important Security Notes:**
- Never commit your real SSN or cookies to version control
- Keep your `config.json` file private and secure
- Session cookies are automatically managed and refreshed by the application
- The application requires valid initial cookies to function

## Project Structure

```
trafikverket-helper/
├── api/                    # API integration modules
│   ├── exceptions.py       # Custom exception classes
│   ├── session_manager.py  # Session and cookie management
│   └── trafikverket.py     # Main API client
├── data/                   # Data storage directory
│   ├── rides.db           # SQLite database for ride data
│   └── valid_locations.json # Valid location IDs
├── helpers/                # Utility modules
│   ├── database.py        # Database operations
│   ├── helpers.py         # General utility functions
│   ├── io.py              # I/O operations and config management
│   └── output.py          # Logging and output formatting
├── log/                   # Application logs
├── modes/                 # Execution modes
│   ├── __init__.py        # Package initialization
│   ├── monitor_rides.py   # Continuous ride monitoring
│   ├── display_rides.py   # View and manage ride data
│   └── web_server.py      # Web server interface (placeholder)
├── tests/                 # Test suite
│   ├── __init__.py        # Test package initialization
│   ├── test_database.py   # Database functionality tests
│   ├── test_session_manager.py # Session management tests
│   ├── test_proactive_refresh.py # Proactive refresh tests
│   ├── test_auto_refresh.py # Auto-refresh functionality tests
│   └── debug_test.py      # Debug and development tests
├── variables/             # Configuration and constants
│   ├── constants.py       # Application constants
│   └── paths.py           # File paths configuration
├── config.json           # Main configuration file
├── main.py               # Application entry point
└── requirements.txt      # Python dependencies
```

## Troubleshooting

### Common Issues

**Session Expired Errors:**
- Sessions are automatically refreshed by the application
- If automatic refresh fails, check the logs for detailed error messages
- Ensure you have valid initial cookies in your `config.json` file
- You may need to manually update cookies from a fresh browser session

**No Rides Found:**
- Check if your examination type is correctly selected
- Verify your location preferences in the configuration
- Try different time ranges in database management mode

**Database Issues:**
- The SQLite database is automatically created on first run
- Use "Database management" mode to view and clean old data
- Database files are stored in the `data/` directory

**API Connection Problems:**
- Check your internet connection
- Ensure your Swedish SSN is correctly formatted
- Verify that your session cookies are valid and not expired

### Getting Help

If you encounter issues:
1. Check the log files in the `log/` directory for detailed error messages
2. Verify your configuration in `config.json`
3. Sessions are automatically managed - check logs for refresh status
4. Use database management tools to inspect stored data

## License

This project is licensed under the MIT License - see the LICENSE file for details.