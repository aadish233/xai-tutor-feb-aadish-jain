"""
Migration: Create products table
Version: 002
Description: Creates the products table for storing product/service information
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
    cursor.execute("SELECT 1 FROM _migrations WHERE name = ?", ("002_create_products_table",))
    if cursor.fetchone():
        print("Migration 002_create_products_table already applied. Skipping.")
        conn.close()
        return
    
    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    
    # Record migration
    cursor.execute(
        "INSERT INTO _migrations (name) VALUES (?)",
        ("002_create_products_table",)
    )
    
    conn.commit()
    conn.close()
    print("Migration 002_create_products_table applied successfully.")


def downgrade():
    """Revert the migration."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute(
        "DELETE FROM _migrations WHERE name = ?",
        ("002_create_products_table",)
    )
    
    conn.commit()
    conn.close()
    print("Migration 002_create_products_table reverted successfully.")
