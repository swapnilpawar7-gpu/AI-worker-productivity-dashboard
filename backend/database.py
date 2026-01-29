"""
Database module for the Worker Productivity Dashboard.
Handles SQLite database initialization, connection management, and schema definition.
"""

import sqlite3
import os

DATABASE_PATH = os.environ.get('DATABASE_PATH', 'productivity.db')


def get_db_connection():
    """
    Create and return a database connection with row factory enabled.
    Row factory allows accessing columns by name.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialize the database schema.
    Creates tables if they don't exist.
    
    Schema:
    - workers: Stores worker information (worker_id, name)
    - workstations: Stores workstation information (station_id, name)
    - events: Stores all AI camera events with timestamps, types, and metadata
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Workers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            worker_id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)
    
    # Workstations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workstations (
            station_id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)
    
    # Events table
    # Note: Using TEXT for timestamp to store ISO 8601 format
    # This allows for proper sorting and parsing while maintaining readability
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            worker_id TEXT NOT NULL,
            station_id TEXT,
            event_type TEXT NOT NULL,
            confidence REAL DEFAULT 0.0,
            count INTEGER,
            FOREIGN KEY (worker_id) REFERENCES workers(worker_id),
            FOREIGN KEY (station_id) REFERENCES workstations(station_id)
        )
    """)
    
    # Create indexes for common query patterns
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_worker 
        ON events(worker_id, timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_station 
        ON events(station_id, timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_timestamp 
        ON events(timestamp)
    """)
    
    # Create unique index for duplicate detection
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_events_duplicate 
        ON events(timestamp, worker_id, event_type)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized at: {DATABASE_PATH}")


if __name__ == '__main__':
    init_db()
    print("Database schema created successfully.")
