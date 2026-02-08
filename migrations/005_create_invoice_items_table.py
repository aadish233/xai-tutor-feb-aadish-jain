"""
Migration: Create invoice items table
Version: 005
Description: Creates the invoice_items table for storing line items in invoices
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
    cursor.execute("SELECT 1 FROM _migrations WHERE name = ?", ("005_create_invoice_items_table",))
    if cursor.fetchone():
        print("Migration 005_create_invoice_items_table already applied. Skipping.")
        conn.close()
        return
    
    # Create invoice_items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    # Record migration
    cursor.execute(
        "INSERT INTO _migrations (name) VALUES (?)",
        ("005_create_invoice_items_table",)
    )
    
    conn.commit()
    conn.close()
    print("Migration 005_create_invoice_items_table applied successfully.")


def downgrade():
    """Revert the migration."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS invoice_items")
    cursor.execute(
        "DELETE FROM _migrations WHERE name = ?",
        ("005_create_invoice_items_table",)
    )
    
    conn.commit()
    conn.close()
    print("Migration 005_create_invoice_items_table reverted successfully.")
