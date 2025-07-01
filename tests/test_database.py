#!/usr/bin/env python3
"""
Test script for the database functionality.
This script tests the basic database operations to ensure everything works correctly.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from helpers.database import RideDatabase


def test_database():
    """Test the database functionality with sample data."""
    
    print("Testing database functionality...")
    
    # Create a test database in a temporary location
    test_db_path = project_root / 'data' / 'test_rides.db'
    
    # Remove test database if it exists
    if test_db_path.exists():
        test_db_path.unlink()
    
    # Initialize database
    db = RideDatabase(str(test_db_path))
    print("✓ Database initialized")
    
    # Sample ride data for Kunskapsprov
    kunskapsprov_rides = [
        {
            "name": "Kunskapsprov B",
            "date": "2025-01-15",
            "time": "10:00",
            "location": "Stockholm",
            "cost": "325kr"
        },
        {
            "name": "Kunskapsprov B", 
            "date": "2025-01-16",
            "time": "14:30",
            "location": "Göteborg",
            "cost": "325kr"
        }
    ]
    
    # Sample ride data for Körprov
    korprov_rides = [
        {
            "name": "Körprov B",
            "date": "2025-01-20",
            "time": "09:15",
            "location": "Malmö",
            "cost": "450kr"
        }
    ]
    
    # Test storing rides for Kunskapsprov
    db.store_rides(kunskapsprov_rides, "Kunskapsprov")
    print("✓ Rides stored successfully")
    
    # Test retrieving all rides
    rides = db.get_all_rides("Kunskapsprov")
    assert len(rides) == 2, f"Expected 2 rides, got {len(rides)}"
    print("✓ Retrieved all rides correctly")
    
    # Test retrieving rides by date range
    rides_in_range = db.get_rides_by_date_range("Kunskapsprov", "2025-01-15", "2025-01-16")
    assert len(rides_in_range) == 2, f"Expected 2 rides in range, got {len(rides_in_range)}"
    print("✓ Date range filtering works")
    
    # Test retrieving rides by location
    stockholm_rides = db.get_rides_by_location("Kunskapsprov", "Stockholm")
    assert len(stockholm_rides) == 1, f"Expected 1 ride in Stockholm, got {len(stockholm_rides)}"
    print("✓ Location filtering works")
    
    # Test getting next available ride
    next_ride = db.get_next_available_ride("Kunskapsprov", current_date="2025-01-01")
    assert next_ride is not None, "Expected to find next available ride"
    print("✓ Next available ride retrieval works")
        
    # Test storing rides for Körprov
    db.store_rides(korprov_rides, "Körprov")
    all_rides = db.get_all_rides("Körprov")
    assert len(all_rides) == 1, f"Expected 1 ride for Körprov, got {len(all_rides)}"
    print("✓ Multiple examination types work")
    
    # Test that Kunskapsprov rides are still there
    kunskapsprov_rides = db.get_all_rides("Körprov")
    assert len(kunskapsprov_rides) == 2, f"Expected 2 rides for Kunskapsprov, got {len(kunskapsprov_rides)}"
    print("✓ Examination types are independent")
    
    # Clean up
    test_db_path.unlink()
    print("✓ Test database cleaned up")
    
    print("\n🎉 All database tests passed!")


if __name__ == "__main__":
    test_database() 