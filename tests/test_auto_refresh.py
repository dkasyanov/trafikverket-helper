#!/usr/bin/env python3
"""
Test script for automatic cookie refresh functionality.
"""

import time
from user_agent import generate_user_agent
from api.trafikverket import TrafikverketAPI
from helpers import io

def test_automatic_refresh():
    """Test that cookies are automatically refreshed during API operations."""
    
    # Load config
    config = io.load_config()
    
    # Generate user agent
    useragent = generate_user_agent()
    
    # Initialize the API
    api = TrafikverketAPI(
        useragent=useragent,
        ssn=config['swedish_ssn']
    )
    
    print("=== Initial Session Info ===")
    session_info = api.get_session_info()
    print(f"Last refresh: {session_info['last_refresh'] or 'Never'}")
    print(f"Minutes until expiration: {session_info.get('minutes_until_expiration', 'Unknown')}")
    print(f"Should refresh: {session_info.get('should_refresh', False)}")
    
    print("\n=== Testing API Call with Auto-Refresh ===")
    
    # Load valid location IDs
    valid_location_ids = io.load_location_ids()
    
    if not valid_location_ids.get('Kunskapsprov'):
        print("No valid location IDs found for testing")
        return
    
    # Test with a small location ID list
    test_location_id = valid_location_ids['Kunskapsprov'][0]
    
    try:
        print(f"Making API call to location {test_location_id}...")
        result = api.get_available_dates(test_location_id, extended_information=False)
        print(f"✅ API call successful! Found {len(result)} available dates.")
        
        # Check if cookies were refreshed during the call
        print("\n=== Post-API Call Session Info ===")
        session_info = api.get_session_info()
        print(f"Last refresh: {session_info['last_refresh'] or 'Never'}")
        print(f"Minutes until expiration: {session_info.get('minutes_until_expiration', 'Unknown')}")
        print(f"Should refresh: {session_info.get('should_refresh', False)}")
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing automatic cookie refresh functionality...")
    print("=" * 50)
    
    try:
        test_automatic_refresh()
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc() 