"""
Migration: Create clients table
Version: 003
Description: Creates the clients table for storing client information
"""

import sqlite3
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DATABASE_PATH


def upgrade():
    """Apply the migration."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check if this migration has already been applied
    cursor.execute("SELECT 1 FROM _migrations WHERE name = ?", ("003_create_clients_table",))
    if cursor.fetchone():
        print("Migration 003_create_clients_table already applied. Skipping.")
        conn.close()
        return
    
    # Create clients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            company_registration_no TEXT NOT NULL
        )
    """)
    
    # Record migration
    cursor.execute(
        "INSERT INTO _migrations (name) VALUES (?)",
        ("003_create_clients_table",)
    )
    
    conn.commit()
    conn.close()
    print("Migration 003_create_clients_table applied successfully.")


def downgrade():
    """Revert the migration."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS clients")
    cursor.execute(
        "DELETE FROM _migrations WHERE name = ?",
        ("003_create_clients_table",)
    )
    
    conn.commit()
    conn.close()
    print("Migration 003_create_clients_table reverted successfully.")
