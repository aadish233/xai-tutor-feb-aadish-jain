"""
Migration: Create invoices table
Version: 004
Description: Creates the invoices table for storing invoice records
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
    cursor.execute("SELECT 1 FROM _migrations WHERE name = ?", ("004_create_invoices_table",))
    if cursor.fetchone():
        print("Migration 004_create_invoices_table already applied. Skipping.")
        conn.close()
        return
    
    # Create invoices table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT NOT NULL UNIQUE,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            client_id INTEGER NOT NULL,
            address TEXT NOT NULL,
            tax REAL NOT NULL DEFAULT 0,
            total REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)
    
    # Record migration
    cursor.execute(
        "INSERT INTO _migrations (name) VALUES (?)",
        ("004_create_invoices_table",)
    )
    
    conn.commit()
    conn.close()
    print("Migration 004_create_invoices_table applied successfully.")


def downgrade():
    """Revert the migration."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS invoices")
    cursor.execute(
        "DELETE FROM _migrations WHERE name = ?",
        ("004_create_invoices_table",)
    )
    
    conn.commit()
    conn.close()
    print("Migration 004_create_invoices_table reverted successfully.")
