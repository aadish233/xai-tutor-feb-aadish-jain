"""
Migration: Seed products and clients
Version: 006
Description: Inserts seed data for products and clients
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
    cursor.execute("SELECT 1 FROM _migrations WHERE name = ?", ("006_seed_products_and_clients",))
    if cursor.fetchone():
        print("Migration 006_seed_products_and_clients already applied. Skipping.")
        conn.close()
        return
    
    # Seed products
    products = [
        ("Web Development", 5000.00),
        ("Mobile App Development", 8000.00),
        ("UI/UX Design", 2500.00),
        ("Cloud Infrastructure Setup", 3500.00),
        ("Database Design & Optimization", 2000.00),
        ("Technical Consulting", 150.00),
        ("Quality Assurance Testing", 1500.00),
        ("Maintenance & Support", 1000.00),
    ]
    
    cursor.executemany(
        "INSERT INTO products (name, price) VALUES (?, ?)",
        products
    )
    
    # Seed clients
    clients = [
        ("Acme Corporation", "123 Business Ave, New York, NY 10001", "ACM-2024-001"),
        ("TechStart Inc.", "456 Innovation Blvd, San Francisco, CA 94105", "TECH-2024-002"),
        ("Global Solutions Ltd.", "789 Commerce Street, London, UK SW1A 1AA", "GLOB-2024-003"),
        ("Bright Ventures LLC", "321 Enterprise Way, Austin, TX 78701", "BRIT-2024-004"),
        ("Coastal Trading Co.", "654 Harbor Road, Miami, FL 33101", "COAST-2024-005"),
    ]
    
    cursor.executemany(
        "INSERT INTO clients (name, address, company_registration_no) VALUES (?, ?, ?)",
        clients
    )
    
    # Record migration
    cursor.execute(
        "INSERT INTO _migrations (name) VALUES (?)",
        ("006_seed_products_and_clients",)
    )
    
    conn.commit()
    conn.close()
    print("Migration 006_seed_products_and_clients applied successfully.")


def downgrade():
    """Revert the migration."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Delete all seed data
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM clients")
    cursor.execute(
        "DELETE FROM _migrations WHERE name = ?",
        ("006_seed_products_and_clients",)
    )
    
    conn.commit()
    conn.close()
    print("Migration 006_seed_products_and_clients reverted successfully.")
