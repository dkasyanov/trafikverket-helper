"""
Database module for persistent storage of ride data.

This module provides functions to store and retrieve ride information
from a SQLite database, allowing the application to persist data
between restarts.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Set
from variables import paths


class RideDatabase:
    """SQLite database handler for ride data persistence."""
    
    def __init__(self, db_path: str = None):
        """Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file. If None, uses default path.
        """
        if db_path is None:
            db_path = paths.project_directory / 'data' / 'rides.db'
        
        # Ensure the data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = str(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create rides table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rides (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    location TEXT NOT NULL,
                    cost TEXT NOT NULL,
                    examination_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_rides_date_time 
                ON rides(date, time)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_rides_examination_type 
                ON rides(examination_type)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_rides_location 
                ON rides(location)
            ''')
            
            conn.commit()
    
    def store_rides(self, rides: List[Dict], examination_type: str):
        """Store a list of rides in the database.
        
        Args:
            rides: List of ride dictionaries
            examination_type: Type of examination (e.g., "Kunskapsprov", "Körprov")
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # First, delete all existing rides for this examination type
            cursor.execute('''
                DELETE FROM rides 
                WHERE examination_type = ?
            ''', (examination_type,))
            
            # Insert new rides
            for ride in rides:
                cursor.execute('''
                    INSERT INTO rides (name, date, time, location, cost, examination_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    ride['name'],
                    ride['date'],
                    ride['time'],
                    ride['location'],
                    ride['cost'],
                    examination_type
                ))
            
            conn.commit()
    
    def get_all_rides(self, examination_type: str) -> List[Dict]:
        """Get all rides for a specific examination type.
        
        Args:
            examination_type: Type of examination
            
        Returns:
            List of ride dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, date, time, location, cost, created_at
                FROM rides 
                WHERE examination_type = ?
                ORDER BY date DESC, time DESC
            ''', (examination_type,))
            
            rows = cursor.fetchall()
            return [
                {
                    'name': row[0],
                    'date': row[1],
                    'time': row[2],
                    'location': row[3],
                    'cost': row[4],
                    'created_at': row[5]
                }
                for row in rows
            ]
    
    def get_rides_by_date_range(self, examination_type: str, start_date: str, end_date: str) -> List[Dict]:
        """Get rides within a date range.
        
        Args:
            examination_type: Type of examination
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of ride dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, date, time, location, cost, created_at
                FROM rides 
                WHERE examination_type = ? AND date BETWEEN ? AND ?
                ORDER BY date ASC, time ASC
            ''', (examination_type, start_date, end_date))
            
            rows = cursor.fetchall()
            return [
                {
                    'name': row[0],
                    'date': row[1],
                    'time': row[2],
                    'location': row[3],
                    'cost': row[4],
                    'created_at': row[5]
                }
                for row in rows
            ]
    
    def get_rides_by_location(self, examination_type: str, location: str) -> List[Dict]:
        """Get rides for a specific location.
        
        Args:
            examination_type: Type of examination
            location: Location name
            
        Returns:
            List of ride dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, date, time, location, cost, created_at
                FROM rides 
                WHERE examination_type = ? AND location = ?
                ORDER BY date ASC, time ASC
            ''', (examination_type, location))
            
            rows = cursor.fetchall()
            return [
                {
                    'name': row[0],
                    'date': row[1],
                    'time': row[2],
                    'location': row[3],
                    'cost': row[4],
                    'created_at': row[5]
                }
                for row in rows
            ]
    
    def get_next_available_ride(self, examination_type: str, current_date: str = None) -> Optional[Dict]:
        """Get the next available ride (earliest date and time).
        
        Args:
            examination_type: Type of examination
            current_date: Date string (YYYY-MM-DD) to use as 'now' (for testing)
        Returns:
            Ride dictionary or None if no rides available
        """
        import datetime
        if current_date is None:
            current_date = datetime.date.today().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, date, time, location, cost, created_at
                FROM rides 
                WHERE examination_type = ? AND date >= ?
                ORDER BY date ASC, time ASC
                LIMIT 1
            ''', (examination_type, current_date))
            row = cursor.fetchone()
            if row:
                return {
                    'name': row[0],
                    'date': row[1],
                    'time': row[2],
                    'location': row[3],
                    'cost': row[4],
                    'created_at': row[5]
                }
            return None
    
    def get_rides_as_set(self, examination_type: str) -> Set[tuple]:
        """Get rides as a set of tuples for comparison operations.
        
        Args:
            examination_type: Type of examination
            
        Returns:
            Set of ride tuples
        """
        rides = self.get_all_rides(examination_type)
        return {tuple(ride.items()) for ride in rides}


# Global database instance
_db_instance = None


def get_database() -> RideDatabase:
    """Get the global database instance.
    
    Returns:
        RideDatabase instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = RideDatabase()
    return _db_instance


def store_rides(rides: List[Dict], examination_type: str):
    """Store rides in the database.
    
    Args:
        rides: List of ride dictionaries
        examination_type: Type of examination
    """
    db = get_database()
    db.store_rides(rides, examination_type)


def get_all_rides(examination_type: str) -> List[Dict]:
    """Get all rides for an examination type.
    
    Args:
        examination_type: Type of examination
        
    Returns:
        List of ride dictionaries
    """
    db = get_database()
    return db.get_all_rides(examination_type)


def get_rides_as_set(examination_type: str) -> Set[tuple]:
    """Get rides as a set for comparison.
    
    Args:
        examination_type: Type of examination
        
    Returns:
        Set of ride tuples
    """
    db = get_database()
    return db.get_rides_as_set(examination_type) 