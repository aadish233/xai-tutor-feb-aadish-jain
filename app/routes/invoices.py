from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import date

from app.database import get_db

router = APIRouter(prefix="/invoices", tags=["invoices"])


# ============================================================================
# Response Models for Related Data
# ============================================================================

class ProductResponse(BaseModel):
    """Schema for product data in invoice items."""
    id: int
    name: str
    price: float


class ClientResponse(BaseModel):
    """Schema for client data in invoice responses."""
    id: int
    name: str
    address: str
    company_registration_no: str


# ============================================================================
# Invoice Item Models
# ============================================================================

class InvoiceItemRequest(BaseModel):
    """Schema for requesting invoice items during invoice creation."""
    product_id: int
    quantity: int


class InvoiceItemResponse(BaseModel):
    """Schema for returning invoice items in responses."""
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float


# ============================================================================
# Invoice Models
# ============================================================================

class InvoiceCreate(BaseModel):
    """Schema for creating a new invoice."""
    client_id: int
    issue_date: str  # Format: YYYY-MM-DD
    due_date: str    # Format: YYYY-MM-DD
    tax: float = 0.0
    items: List[InvoiceItemRequest]


class InvoiceResponse(BaseModel):
    """Schema for returning invoice details."""
    id: int
    invoice_no: str
    issue_date: str
    due_date: str
    client: ClientResponse
    address: str
    items: List[InvoiceItemResponse]
    tax: float
    total: float


class InvoiceListItem(BaseModel):
    """Schema for invoice in list response."""
    id: int
    invoice_no: str
    issue_date: str
    due_date: str
    client_name: str
    total: float


class InvoiceListResponse(BaseModel):
    """Schema for listing invoices."""
    invoices: List[InvoiceListItem]


# ============================================================================
# Helper Functions
# ============================================================================

def get_next_invoice_number(conn) -> str:
    """Generate the next invoice number (INV-001, INV-002, etc.)."""
    cursor = conn.cursor()
    # Get the highest invoice number to avoid duplicates even if invoices are deleted
    cursor.execute(
        "SELECT COALESCE(MAX(CAST(SUBSTR(invoice_no, 5) AS INTEGER)), 0) as max_num FROM invoices"
    )
    max_num = cursor.fetchone()["max_num"]
    invoice_number = max_num + 1
    return f"INV-{invoice_number:03d}"


def validate_invoice_input(conn, invoice: InvoiceCreate):
    """Validate invoice input data before processing."""
    cursor = conn.cursor()
    
    # Validate dates format (YYYY-MM-DD)
    try:
        issue_parts = invoice.issue_date.split("-")
        due_parts = invoice.due_date.split("-")
        if len(issue_parts) != 3 or len(due_parts) != 3:
            raise ValueError()
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Dates must be in format YYYY-MM-DD")
    
    # Validate due_date is after or equal to issue_date
    if invoice.due_date < invoice.issue_date:
        raise HTTPException(status_code=400, detail="Due date must be after or equal to issue date")
    
    # Validate client exists
    cursor.execute("SELECT id FROM clients WHERE id = ?", (invoice.client_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=400, detail=f"Client {invoice.client_id} not found")
    
    # Validate items are not empty
    if not invoice.items:
        raise HTTPException(status_code=400, detail="Invoice must have at least one item")
    
    # Validate tax is not negative
    if invoice.tax < 0:
        raise HTTPException(status_code=400, detail="Tax cannot be negative")
    
    # Validate all products exist and quantities are valid
    for idx, item in enumerate(invoice.items):
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail=f"Item {idx + 1}: Quantity must be greater than 0")
        
        cursor.execute("SELECT id FROM products WHERE id = ?", (item.product_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("", status_code=201)
def create_invoice(invoice: InvoiceCreate):
    """
    Create a new invoice.
    
    Request body:
    - client_id: ID of the client
    - issue_date: Invoice issue date (YYYY-MM-DD)
    - due_date: Invoice due date (YYYY-MM-DD)
    - tax: Tax amount (optional, default 0)
    - items: List of items with product_id and quantity
    
    Returns: Invoice details with generated invoice number
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Validate all input data
            validate_invoice_input(conn, invoice)
            
            # Get client address for invoice
            cursor.execute("SELECT address FROM clients WHERE id = ?", (invoice.client_id,))
            client = cursor.fetchone()
            
            # Generate invoice number
            invoice_no = get_next_invoice_number(conn)
            
            # Calculate total
            subtotal = 0.0
            for item in invoice.items:
                cursor.execute("SELECT price FROM products WHERE id = ?", (item.product_id,))
                product_price = cursor.fetchone()["price"]
                subtotal += product_price * item.quantity
            
            total = subtotal + invoice.tax
            
            # Insert invoice
            cursor.execute(
                """
                INSERT INTO invoices 
                (invoice_no, issue_date, due_date, client_id, address, tax, total)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (invoice_no, invoice.issue_date, invoice.due_date, 
                 invoice.client_id, client["address"], invoice.tax, total)
            )
            
            invoice_id = cursor.lastrowid
            
            # Insert invoice items
            for item in invoice.items:
                cursor.execute("SELECT price FROM products WHERE id = ?", (item.product_id,))
                product_price = cursor.fetchone()["price"]
                subtotal = product_price * item.quantity
                
                cursor.execute(
                    """
                    INSERT INTO invoice_items 
                    (invoice_id, product_id, quantity, unit_price, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (invoice_id, item.product_id, item.quantity, product_price, subtotal)
                )
            
            # Fetch and return the created invoice (within same transaction)
            cursor.execute(
                """
                SELECT i.id, i.invoice_no, i.issue_date, i.due_date, 
                       i.client_id, i.address, i.tax, i.total,
                       c.name as client_name, c.address as client_address, 
                       c.company_registration_no
                FROM invoices i
                JOIN clients c ON i.client_id = c.id
                WHERE i.id = ?
                """,
                (invoice_id,)
            )
            invoice_row = cursor.fetchone()
            
            # Fetch invoice items
            cursor.execute(
                """
                SELECT ii.id, ii.product_id, p.name as product_name,
                       ii.quantity, ii.unit_price, ii.subtotal
                FROM invoice_items ii
                JOIN products p ON ii.product_id = p.id
                WHERE ii.invoice_id = ?
                ORDER BY ii.id
                """,
                (invoice_id,)
            )
            items_rows = cursor.fetchall()
            
            # Build response
            items = [
                {
                    "id": row["id"],
                    "product_id": row["product_id"],
                    "product_name": row["product_name"],
                    "quantity": row["quantity"],
                    "unit_price": row["unit_price"],
                    "subtotal": row["subtotal"]
                }
                for row in items_rows
            ]
            
            client = {
                "id": invoice.client_id,
                "name": invoice_row["client_name"],
                "address": invoice_row["client_address"],
                "company_registration_no": invoice_row["company_registration_no"]
            }
            
            return {
                "id": invoice_row["id"],
                "invoice_no": invoice_row["invoice_no"],
                "issue_date": invoice_row["issue_date"],
                "due_date": invoice_row["due_date"],
                "client": client,
                "address": invoice_row["address"],
                "items": items,
                "tax": invoice_row["tax"],
                "total": invoice_row["total"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("")
def list_invoices():
    """
    List all invoices.
    
    Returns: List of invoices with basic information
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT i.id, i.invoice_no, i.issue_date, i.due_date, 
                       c.name as client_name, i.total
                FROM invoices i
                JOIN clients c ON i.client_id = c.id
                ORDER BY i.id DESC
                """
            )
            rows = cursor.fetchall()
            
            invoices = [
                {
                    "id": row["id"],
                    "invoice_no": row["invoice_no"],
                    "issue_date": row["issue_date"],
                    "due_date": row["due_date"],
                    "client_name": row["client_name"],
                    "total": row["total"]
                }
                for row in rows
            ]
            
            return {"invoices": invoices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{invoice_id}")
def get_invoice(invoice_id: int):
    """
    Get a specific invoice by ID.
    
    Returns: Complete invoice details including items and client information
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Fetch invoice with client info
            cursor.execute(
                """
                SELECT i.id, i.invoice_no, i.issue_date, i.due_date, 
                       i.client_id, i.address, i.tax, i.total,
                       c.id as client_id, c.name as client_name, 
                       c.address as client_address, c.company_registration_no
                FROM invoices i
                JOIN clients c ON i.client_id = c.id
                WHERE i.id = ?
                """,
                (invoice_id,)
            )
            invoice_row = cursor.fetchone()
            
            if not invoice_row:
                raise HTTPException(status_code=404, detail="Invoice not found")
            
            # Fetch invoice items
            cursor.execute(
                """
                SELECT ii.id, ii.product_id, p.name as product_name,
                       ii.quantity, ii.unit_price, ii.subtotal
                FROM invoice_items ii
                JOIN products p ON ii.product_id = p.id
                WHERE ii.invoice_id = ?
                ORDER BY ii.id
                """,
                (invoice_id,)
            )
            items_rows = cursor.fetchall()
            
            # Build response
            items = [
                {
                    "id": row["id"],
                    "product_id": row["product_id"],
                    "product_name": row["product_name"],
                    "quantity": row["quantity"],
                    "unit_price": row["unit_price"],
                    "subtotal": row["subtotal"]
                }
                for row in items_rows
            ]
            
            client = {
                "id": invoice_row["client_id"],
                "name": invoice_row["client_name"],
                "address": invoice_row["client_address"],
                "company_registration_no": invoice_row["company_registration_no"]
            }
            
            return {
                "id": invoice_row["id"],
                "invoice_no": invoice_row["invoice_no"],
                "issue_date": invoice_row["issue_date"],
                "due_date": invoice_row["due_date"],
                "client": client,
                "address": invoice_row["address"],
                "items": items,
                "tax": invoice_row["tax"],
                "total": invoice_row["total"]
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.delete("/{invoice_id}", status_code=204)
def delete_invoice(invoice_id: int):
    """
    Delete an invoice.
    
    Removes the invoice and all associated items.
    Returns: 204 No Content (empty response)
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if invoice exists
            cursor.execute("SELECT id FROM invoices WHERE id = ?", (invoice_id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Invoice not found")
            
            # Delete invoice items (cascade delete)
            cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
            
            # Delete invoice
            cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
            
            return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
