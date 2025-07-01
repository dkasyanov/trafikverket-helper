import re
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional
import requests
import json
import time

from variables import constants
from helpers import io


class SessionManager:
    """Manages session cookies and automatic refresh for Trafikverket API."""
    
    def __init__(self):
        """Initialize the session manager."""
        # Load cookies from config.json
        try:
            config = io.load_config()
            if 'cookies' in config and config['cookies']:
                self.current_cookies = config['cookies'].copy()
                print(f"Loaded {len(self.current_cookies)} cookies from config.json")
            else:
                self.current_cookies = {}
                print("No cookies found in config.json - starting with empty cookies")
        except Exception as e:
            print(f"Error loading config: {e}")
            self.current_cookies = {}
        
        self.last_refresh_time = None
        self.refresh_interval = timedelta(minutes=5)  # Refresh every 5 minutes
        self.session = requests.session()
        
        # Background refresh thread
        self.background_thread = None
        self.background_running = False
        self.background_interval = 300  # 5 minutes in seconds
        
        # Set up session headers for cookie refresh requests
        self.session.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://fp.trafikverket.se',
            'Pragma': 'no-cache',
            'Referer': 'https://fp.trafikverket.se/Boka/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }
        
    def extract_cookies_from_request(self, request_text: str) -> Dict[str, str]:
        """
        Extract cookies from HTTP request text.
        
        Args:
            request_text: Raw HTTP request text
            
        Returns:
            Dictionary of cookie name-value pairs
        """
        cookies = {}
        
        # Find Cookie header
        cookie_match = re.search(r'Cookie:\s*(.+?)(?:\r?\n|$)', request_text, re.IGNORECASE)
        if cookie_match:
            cookie_string = cookie_match.group(1)
            
            # Parse individual cookies
            for cookie in cookie_string.split(';'):
                cookie = cookie.strip()
                if '=' in cookie:
                    name, value = cookie.split('=', 1)
                    cookies[name.strip()] = value.strip()
        
        return cookies
    
    def extract_cookies_from_response(self, response_text: str) -> Dict[str, str]:
        """
        Extract cookies from HTTP response text.
        
        Args:
            response_text: Raw HTTP response text
            
        Returns:
            Dictionary of cookie name-value pairs
        """
        cookies = {}
        
        # Find Set-Cookie headers
        set_cookie_matches = re.findall(r'Set-Cookie:\s*(.+?)(?:\r?\n|$)', response_text, re.IGNORECASE)
        for match in set_cookie_matches:
            cookie_string = match.strip()
            # Extract name and value (before any attributes)
            if '=' in cookie_string:
                name_value = cookie_string.split(';')[0]
                if '=' in name_value:
                    name, value = name_value.split('=', 1)
                    cookies[name.strip()] = value.strip()
        
        return cookies
    
    def update_cookies_from_request(self, request_text: str) -> bool:
        """
        Update cookies from HTTP request text.
        
        Args:
            request_text: Raw HTTP request text
            
        Returns:
            True if cookies were updated, False otherwise
        """
        new_cookies = self.extract_cookies_from_request(request_text)
        if new_cookies:
            return self.update_cookies(new_cookies)
        return False
    
    def update_cookies_from_response(self, response_text: str) -> bool:
        """
        Update cookies from HTTP response text.
        
        Args:
            response_text: Raw HTTP response text
            
        Returns:
            True if cookies were updated, False otherwise
        """
        new_cookies = self.extract_cookies_from_response(response_text)
        if new_cookies:
            return self.update_cookies(new_cookies)
        return False
    
    def update_cookies(self, new_cookies: Dict[str, str]) -> bool:
        """
        Update current cookies with new ones.
        
        Args:
            new_cookies: Dictionary of new cookie name-value pairs
            
        Returns:
            True if cookies were updated, False otherwise
        """
        if new_cookies:
            # Update current cookies with new ones
            self.current_cookies.update(new_cookies)
            self.last_refresh_time = datetime.now()
            print(f"Cookies updated at {self.last_refresh_time}")
            return True
        return False
    
    def parse_cookie_expiration(self, cookie_string: str) -> Optional[datetime]:
        """
        Parse expiration time from a Set-Cookie header.
        
        Args:
            cookie_string: The Set-Cookie header value
            
        Returns:
            datetime object of expiration time, or None if not found
        """
        # Look for expires= attribute
        expires_match = re.search(r'expires=([^;]+)', cookie_string, re.IGNORECASE)
        if expires_match:
            try:
                # Parse the expiration date (format: Fri, 20-Jun-2025 14:48:56 GMT)
                expiration_str = expires_match.group(1).strip()
                return datetime.strptime(expiration_str, '%a, %d-%b-%Y %H:%M:%S %Z')
            except ValueError:
                pass
        return None

    def get_earliest_cookie_expiration(self) -> Optional[datetime]:
        """
        Get the earliest expiration time among current cookies.
        
        Returns:
            datetime of earliest expiration, or None if no expiration found
        """
        earliest_expiration = None
        
        # Check LoginValid cookie format (YYYY-MM-DD HH:MM)
        login_valid = self.current_cookies.get('LoginValid')
        if login_valid:
            try:
                # Parse LoginValid format: "2025-06-20 16:48"
                expiration = datetime.strptime(login_valid, '%Y-%m-%d %H:%M')
                earliest_expiration = expiration
            except ValueError:
                pass
        
        return earliest_expiration

    def should_refresh_cookies(self) -> bool:
        """
        Check if cookies should be refreshed based on expiration time.
        
        Returns:
            True if cookies should be refreshed, False otherwise
        """
        # Check time-based refresh interval (every 5 minutes)
        if (self.last_refresh_time and 
            datetime.now() - self.last_refresh_time > self.refresh_interval):
            return True
        
        # Check if cookies are close to expiring (within 15 minutes)
        earliest_expiration = self.get_earliest_cookie_expiration()
        if earliest_expiration:
            time_until_expiration = earliest_expiration - datetime.now()
            if time_until_expiration < timedelta(minutes=15):
                print(f"Cookies expire in {time_until_expiration}, refreshing automatically...")
                return True
        
        return False

    def ensure_fresh_cookies(self) -> bool:
        """
        Ensure cookies are fresh by checking and refreshing if needed.
        This method is called automatically before API operations.
        
        Returns:
            True if cookies are fresh (either were already fresh or refreshed successfully), False otherwise
        """
        if self.should_refresh_cookies():
            return self.refresh_cookies_proactively()
        return True  # Cookies are still fresh

    def refresh_cookies_proactively(self) -> bool:
        """
        Proactively refresh cookies using the /Boka/getCookie endpoint.
        
        Returns:
            True if cookies were successfully refreshed, False otherwise
        """
        try:
            # Prepare cookies for the request
            cookie_string = '; '.join([f"{name}={value}" for name, value in self.current_cookies.items()])
            
            # Make request to getCookie endpoint
            response = self.session.post(
                url='https://fp.trafikverket.se/Boka/getCookie',
                json={"key": "LoginValid"},
                headers={'Cookie': cookie_string},
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                # Extract new cookies from response headers
                new_cookies = {}
                for header, value in response.headers.items():
                    if header.lower() == 'set-cookie':
                        # Parse the cookie
                        if '=' in value:
                            name_value = value.split(';')[0]
                            if '=' in name_value:
                                name, cookie_value = name_value.split('=', 1)
                                new_cookies[name.strip()] = cookie_value.strip()
                
                if new_cookies:
                    # Update current cookies
                    self.current_cookies.update(new_cookies)
                    self.last_refresh_time = datetime.now()
                    print(f"Proactively refreshed cookies at {self.last_refresh_time}")
                    
                    # Save updated cookies to config
                    try:
                        config = io.load_config()
                        config['cookies'] = self.current_cookies
                        io.update_config(config)
                        print("Updated cookies saved to config.json")
                    except Exception as e:
                        print(f"Failed to save cookies to config: {e}")
                    
                    return True
                else:
                    print("No new cookies found in response")
                    return False
            else:
                print(f"Failed to refresh cookies: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error refreshing cookies proactively: {e}")
            return False

    def is_session_expired(self, response_text: str = None) -> bool:
        """
        Check if the current session is expired.
        
        Args:
            response_text: Optional response text to check for error messages
            
        Returns:
            True if session is expired, False otherwise
        """
        # Check if we need to refresh based on time or expiration
        if self.should_refresh_cookies():
            # Try to refresh proactively
            if self.refresh_cookies_proactively():
                return False  # Successfully refreshed, not expired
            else:
                return True  # Failed to refresh, consider expired
        
        # Check response for session expiration indicators
        if response_text:
            # Look for common session expiration patterns
            expired_patterns = [
                r'session.*expired',
                r'login.*required',
                r'unauthorized',
                r'401',
                r'403',
                r'nullreferenceexception',
                r'status.*500'
            ]
            
            for pattern in expired_patterns:
                if re.search(pattern, response_text, re.IGNORECASE):
                    return True
        
        return False
    
    def get_current_cookies(self) -> Dict[str, str]:
        """
        Get current cookies in memory.
        
        Returns:
            Dictionary of current cookies
        """
        return self.current_cookies.copy()
    
    def validate_cookies(self, cookies: Dict[str, str]) -> bool:
        """
        Validate that cookies contain required fields.
        
        Args:
            cookies: Dictionary of cookies to validate
            
        Returns:
            True if cookies are valid, False otherwise
        """
        required_cookies = [
            'FpsPartnerDeviceIdentifier',
            'LoginValid',
            'FpsExternalIdentity',
            'ASP.NET_SessionId'
        ]
        
        for cookie_name in required_cookies:
            if cookie_name not in cookies:
                return False
        
        return True
    
    def get_session_info(self) -> Dict:
        """
        Get information about the current session.
        
        Returns:
            Dictionary with session information
        """
        earliest_expiration = self.get_earliest_cookie_expiration()
        time_until_expiration = None
        if earliest_expiration:
            time_until_expiration = (earliest_expiration - datetime.now()).total_seconds() / 60  # minutes
        
        info = {
            'last_refresh': self.last_refresh_time.isoformat() if self.last_refresh_time else None,
            'refresh_interval_hours': self.refresh_interval.total_seconds() / 3600,
            'cookies_count': len(self.current_cookies),
            'has_required_cookies': self.validate_cookies(self.current_cookies),
            'login_valid_until': self.current_cookies.get('LoginValid', 'Unknown'),
            'earliest_expiration': earliest_expiration.isoformat() if earliest_expiration else None,
            'minutes_until_expiration': time_until_expiration,
            'should_refresh': self.should_refresh_cookies(),
            'current_cookies': self.current_cookies
        }
        
        return info

    def start_background_refresh(self, interval_seconds: int = 300):
        """
        Start background thread to periodically refresh cookies.
        
        Args:
            interval_seconds: How often to check for refresh (default: 5 minutes)
        """
        if self.background_running:
            print("Background refresh already running")
            return
        
        self.background_interval = interval_seconds
        self.background_running = True
        self.background_thread = threading.Thread(target=self._background_refresh_loop, daemon=True)
        self.background_thread.start()
        print(f"Started background cookie refresh (checking every {interval_seconds} seconds)")

    def stop_background_refresh(self):
        """Stop the background refresh thread."""
        self.background_running = False
        if self.background_thread:
            self.background_thread.join(timeout=1)
        print("Stopped background cookie refresh")

    def _background_refresh_loop(self):
        """Background loop for periodic cookie refresh."""
        while self.background_running:
            try:
                # Check if we should refresh
                if self.should_refresh_cookies():
                    print("Background: Refreshing cookies...")
                    if self.refresh_cookies_proactively():
                        print("Background: Cookies refreshed successfully")
                    else:
                        print("Background: Failed to refresh cookies")
                
                # Sleep for the specified interval
                time.sleep(self.background_interval)
                
            except Exception as e:
                print(f"Background refresh error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying


# Global session manager instance
_session_manager = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def refresh_cookies_from_request(request_text: str) -> bool:
    """
    Convenience function to refresh cookies from HTTP request text.
    
    Args:
        request_text: Raw HTTP request text
        
    Returns:
        True if cookies were updated, False otherwise
    """
    return get_session_manager().update_cookies_from_request(request_text)


def refresh_cookies_from_response(response_text: str) -> bool:
    """
    Convenience function to refresh cookies from HTTP response text.
    
    Args:
        response_text: Raw HTTP response text
        
    Returns:
        True if cookies were updated, False otherwise
    """
    return get_session_manager().update_cookies_from_response(response_text) 