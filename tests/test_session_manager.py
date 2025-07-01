#!/usr/bin/env python3
"""
Test script for the session manager functionality.
"""

from api.session_manager import get_session_manager


def test_session_manager():
    """Test the session manager functionality."""
    print("=== Testing Session Manager ===")
    
    # Get session manager
    session_manager = get_session_manager()
    
    # Test initial state
    print("\n1. Testing initial state:")
    session_info = session_manager.get_session_info()
    print(f"   Cookies count: {session_info['cookies_count']}")
    print(f"   Has required cookies: {session_info['has_required_cookies']}")
    print(f"   Last refresh: {session_info['last_refresh']}")
    
    # Test cookie extraction from request
    print("\n2. Testing cookie extraction from request:")
    test_request = """POST /Boka/occasion-bundles HTTP/1.1
Accept: application/json, text/plain, */*
Cookie: FpsPartnerDeviceIdentifier=TEST123; LoginValid=2025-06-19 10:00; FpsExternalIdentity=TEST456
Content-Type: application/json; charset=UTF-8
Host: fp.trafikverket.se"""
    
    cookies = session_manager.extract_cookies_from_request(test_request)
    print(f"   Extracted cookies: {cookies}")
    
    # Test cookie extraction from response
    print("\n3. Testing cookie extraction from response:")
    test_response = """HTTP/1.1 200 OK
Content-Type: application/json
Set-Cookie: LoginValid=2025-06-19 11:00; expires=Fri, 19-Jul-2025 10:00:00 GMT; path=/; HttpOnly
Set-Cookie: FpsExternalIdentity=NEW789; expires=Fri, 19-Jul-2025 10:00:00 GMT; path=/; HttpOnly
Server: Microsoft-IIS/10.0"""
    
    cookies = session_manager.extract_cookies_from_response(test_response)
    print(f"   Extracted cookies: {cookies}")
    
    # Test session expiration detection
    print("\n4. Testing session expiration detection:")
    expired_response = '{"status":500,"data":null,"type":"NullReferenceException"}'
    is_expired = session_manager.is_session_expired(expired_response)
    print(f"   Detected expired session: {is_expired}")
    
    valid_response = '{"status":200,"data":{"bundles":[]}}'
    is_expired = session_manager.is_session_expired(valid_response)
    print(f"   Detected valid session: {is_expired}")
    
    print("\n=== Session Manager Test Complete ===")


if __name__ == "__main__":
    test_session_manager() 