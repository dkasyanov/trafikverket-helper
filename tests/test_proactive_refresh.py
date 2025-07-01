#!/usr/bin/env python3
"""
Test script for proactive cookie refresh functionality.
"""

import time
from api.trafikverket import TrafikverketAPI
from variables import constants

def test_proactive_refresh():
    """Test the proactive cookie refresh functionality."""
    
    # Initialize the API
    api = TrafikverketAPI(
        useragent=constants.useragent,
        ssn=constants.ssn
    )
    
    print("=== Initial Session Info ===")
    session_info = api.get_session_info()
    for key, value in session_info.items():
        if key != 'current_cookies':  # Skip printing all cookies
            print(f"{key}: {value}")
    
    print("\n=== Testing Proactive Refresh ===")
    
    # Test manual proactive refresh
    print("Attempting manual proactive refresh...")
    success = api.refresh_cookies_proactively()
    print(f"Manual refresh result: {success}")
    
    if success:
        print("\n=== Updated Session Info ===")
        session_info = api.get_session_info()
        for key, value in session_info.items():
            if key != 'current_cookies':  # Skip printing all cookies
                print(f"{key}: {value}")
    
    print("\n=== Testing Automatic Refresh Check ===")
    
    # Test if session is expired (this should trigger proactive refresh if needed)
    is_expired = api.session_manager.is_session_expired()
    print(f"Session expired check: {is_expired}")
    
    # Show final session info
    print("\n=== Final Session Info ===")
    session_info = api.get_session_info()
    for key, value in session_info.items():
        if key != 'current_cookies':  # Skip printing all cookies
            print(f"{key}: {value}")

def test_continuous_monitoring():
    """Test continuous monitoring with periodic checks."""
    
    print("=== Continuous Monitoring Test ===")
    print("This will check session status every 30 seconds for 2 minutes...")
    
    api = TrafikverketAPI(
        useragent=constants.useragent,
        ssn=constants.ssn
    )
    
    for i in range(4):  # 4 checks over 2 minutes
        print(f"\n--- Check {i+1}/4 ---")
        
        session_info = api.get_session_info()
        print(f"Should refresh: {session_info.get('should_refresh', False)}")
        print(f"Minutes until expiration: {session_info.get('minutes_until_expiration', 'Unknown')}")
        
        # Check if session is expired (this will trigger refresh if needed)
        is_expired = api.session_manager.is_session_expired()
        print(f"Session expired: {is_expired}")
        
        if i < 3:  # Don't sleep after the last check
            print("Waiting 30 seconds...")
            time.sleep(30)

if __name__ == "__main__":
    print("Testing proactive cookie refresh functionality...")
    print("=" * 50)
    
    try:
        test_proactive_refresh()
        print("\n" + "=" * 50)
        test_continuous_monitoring()
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc() 