# Trafikverket Helper

[![Version](https://img.shields.io/github/v/release/ekvanox/trafikverket-helper)](https://img.shields.io/github/v/release/ekvanox/trafikverket-helper)
![GitHub repo size](https://img.shields.io/github/repo-size/ekvanox/trafikverket-helper)
[![CodeFactor](https://www.codefactor.io/repository/github/ekvanox/trafikverket-helper/badge)](https://www.codefactor.io/repository/github/ekvanox/trafikverket-helper)
![License](https://img.shields.io/github/license/ekvanox/trafikverket-helper)

A Python tool for monitoring and finding available Swedish driving examination appointments through the Trafikverket API. Never miss an available slot again!

## ✨ Key Features

- **🔄 Automatic Session Management**: Handles cookie refresh automatically - no manual intervention required
- **💾 Persistent Storage**: SQLite database preserves your ride data between restarts
- **📊 Multiple Viewing Modes**: Monitor continuously, display stored data, or use web interface
- **🎯 Smart Filtering**: Filter by location, date range, and examination type
- **🔍 Real-time Monitoring**: Get notified of new or removed ride availability

![Usage example gif](https://github.com/ekvanox/trafikverket-helper/blob/master/images/usage.gif?raw=true)

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Valid Swedish Social Security Number (personnummer)
- Active Trafikverket account with valid session cookies

### Installation

1. **Clone and install dependencies:**
   ```bash
   git clone https://github.com/ekvanox/trafikverket-helper
   cd trafikverket-helper
   pip install -r requirements.txt
   ```

2. **Set up configuration:**
   ```bash
   cp config.json.example config.json
   # Edit config.json with your SSN and session cookies (see Configuration section)
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### First Run
1. Select examination type: `Kunskapsprov` (theory) or `Körprov` (practical)
2. Choose execution mode: Monitor, Display, or Web Server
3. Follow the interactive prompts

## 📋 Execution Modes

### 🔍 Monitor Rides
Continuously monitors ride availability and logs changes in real-time:
- Automatically detects new and removed rides
- Persists all data to SQLite database
- Background session refresh every 5 minutes
- Perfect for long-running monitoring sessions

### 📊 Display Rides  
View and manage your stored ride data:
- **View all rides** for selected examination type
- **Filter by date range** to see rides within specific periods
- **Filter by location** to focus on preferred test centers
- **Database cleanup** to remove old rides
- **Statistics view** showing data summary

### 🌐 Web Server
Launch a local web interface to view rides in your browser:
- Clean, responsive web interface
- Real-time data from your SQLite database
- Easy sharing and viewing of available slots

> **⚠️ Note**: Web server mode is not yet implemented. This feature will be added in future releases.

## 🔐 Session Management

The application provides **fully automatic session management** - no manual cookie refresh needed!

### How It Works
1. **Smart Detection**: Monitors session validity continuously
2. **Proactive Refresh**: Refreshes cookies 15 minutes before expiration
3. **Background Process**: Runs automatic refresh every 5 minutes during monitoring
4. **Error Recovery**: Automatically recovers from unexpected session expiration
5. **Zero Maintenance**: Once configured, runs indefinitely without intervention

### ⚠️ Important: Initial Setup Required
The application **cannot generate initial cookies** - you must provide them:
- Cookies must be obtained from an authenticated Trafikverket browser session
- See the Configuration section below for detailed cookie setup instructions

## 💾 Database Storage

The application uses **SQLite database** (`data/rides.db`) for persistent data storage:

### Benefits
- **Data Persistence**: Ride data preserved between application restarts
- **Historical Analysis**: View and analyze ride availability trends over time  
- **Faster Performance**: Load cached data instead of API calls on every startup
- **Automatic Management**: Database created automatically on first run
- **Easy Cleanup**: Built-in tools to remove old rides and manage database size

### Database Features
- Automatic schema creation and migration
- Efficient indexing for fast queries
- Data integrity validation
- Automatic backup and recovery

## ⚙️ Configuration

### Config File Setup
Create `config.json` from the example template:

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

### 🍪 Cookie Setup (Critical Step)

**Why cookies are needed:** The application cannot log in automatically - it needs valid session cookies from your authenticated browser session.

**Step-by-step cookie extraction:**

1. **Login to Trafikverket**
   - Go to [Trafikverket's booking system](https://fp.trafikverket.se/)
   - Log in with your credentials

2. **Open Developer Tools**
   - Press `F12` or right-click → "Inspect"
   - Go to the **Network** tab

3. **Capture a Request**
   - Navigate within the booking system (click any menu item)
   - Find any request in the Network tab
   - Right-click on a request → **Copy** → **Copy as cURL**

4. **Extract Cookies**
   - Paste the cURL command in a text editor
   - Find the `-H 'Cookie: ...'` section
   - Copy the cookie values and add them to your `config.json`

### Required Fields
- **`swedish_ssn`**: Your personnummer (format: `YYYYMMDD-XXXX`)
- **`cookies`**: All cookies from your authenticated browser session

### 🔒 Security Notes
- **Never commit real credentials** to version control
- Keep `config.json` private and secure  
- Cookies are automatically refreshed by the application
- Add `config.json` to your `.gitignore` file

## 📁 Project Structure

```
trafikverket-helper/
├── 🚀 main.py                     # Application entry point
├── ⚙️ config.json                 # Configuration file (create from example)
├── 📋 requirements.txt            # Python dependencies
│
├── 🔌 api/                        # API integration
│   ├── trafikverket.py           # Main API client  
│   ├── session_manager.py        # Cookie & session management
│   └── exceptions.py             # Custom exceptions
│
├── 🎯 modes/                      # Execution modes
│   ├── monitor_rides.py          # Real-time monitoring
│   ├── display_rides.py          # Data viewing & management
│   └── web_server.py             # Web interface
│
├── 🛠️ helpers/                    # Utility modules
│   ├── database.py               # SQLite operations
│   ├── io.py                     # Config & file I/O
│   ├── output.py                 # Logging & formatting
│   └── helpers.py                # General utilities
│
├── 💾 data/                       # Data storage
│   ├── rides.db                  # SQLite database (auto-created)
│   └── valid_locations.json      # Location IDs
│
├── 🧪 tests/                      # Test suite
│   ├── test_database.py          # Database tests
│   ├── test_session_manager.py   # Session tests
│   └── test_*.py                 # Other test modules
│
├── 📊 log/                        # Application logs
└── 🔧 variables/                  # Constants & configuration
    ├── constants.py              # App constants
    └── paths.py                  # File paths
```

## 🔧 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **🚫 Session Expired Errors** | Check logs in `log/` directory. Usually means initial cookies in `config.json` are invalid. Extract fresh cookies from browser. |
| **📭 No Rides Found** | Normal - means no slots available! Try different examination types or check during different times of day. |
| **💾 Database Issues** | Database auto-creates on first run. Use "Display rides" mode → "Database statistics" to verify data. |
| **🌐 Connection Problems** | Verify internet connection and that Trafikverket website is accessible. Check if cookies are expired. |
| **⚙️ Config Issues** | Ensure `config.json` exists with valid SSN format (`YYYYMMDD-XXXX`) and fresh cookies. |

### 🆘 Getting Help

**Step-by-step debugging:**
1. **Check logs**: Look in `log/` directory for detailed error messages
2. **Verify config**: Ensure `config.json` has valid SSN and recent cookies  
3. **Test connection**: Try accessing Trafikverket website manually
4. **Fresh cookies**: Extract new cookies if issues persist
5. **Database check**: Use "Display rides" mode to verify data storage

**Still stuck?** Create an issue with:
- Error message from logs
- Your execution mode  
- Steps to reproduce (without sharing personal data)

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

### Development Setup
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/trafikverket-helper
cd trafikverket-helper

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**⚠️ Disclaimer:** This tool is for educational and personal use only. Users are responsible for complying with Trafikverket's terms of service and applicable laws. The authors are not responsible for any misuse of this tool.