# Invoicing System Backend - Backend Assessment

**Time Limit: 60 minutes**

## Important Instructions

> **1. Fork this repo into your personal github account**
> 
> **2. Do not raise Pull Request in the original repo**
> 
> **3. Application must be runnable with `docker-compose up` command**
> 
> **4. Complete as many APIs as possible within the time limit**
> 
> **5. Prioritize working functionality - do not submit broken code that fails to run with `docker-compose up`**

### Tips
- Focus on core functionality first, then add features incrementally
- Test your application with `docker-compose up` before final submission
- A partially complete but working solution is better than a complete but broken one

---

A FastAPI backend project with SQLite database.

## Objective

Build a backend API for an **Invoicing System** that allows users to create and manage invoices.

## Functional Requirements

### Single User System
- No authentication required. The system is designed for a single user.

### Invoice Management
- User should be able to create invoices
- User should be able to list invoices
- User should be able to get an invoice by ID
- User should be able to delete an invoice

An invoice consists of:
- **Client**
- **Products** (items)

For **products** and **clients**, do not create APIs—use seed data. The developer needs to design the database schema and APIs for the invoicing system.



## Data Requirements (Fields)

### Product (seed data only)
- name
- price

### Client (seed data only)
- name
- address
- company registration no.

### Invoice
- Invoice no
- issue date
- due date
- client
- address
- items
- tax
- total

## Quick Start (Docker)

The easiest way to run the application:

```bash
docker-compose up --build
```

This will:
- Build the Docker image
- Run database migrations automatically (if applicable)
- Start the API server at `http://localhost:8000`

To stop the application:

```bash
docker-compose down
```

## Manual Setup (Without Docker)

### 1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run database migrations (if applicable)

```bash
python migrate.py upgrade
```

### 4. Start the server

```bash
uvicorn app.main:app --reload
```

Or run directly:

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

## Database Migrations

### Running Migrations

**Apply all pending migrations:**
```bash
python migrate.py upgrade
```

**Revert all migrations:**
```bash
python migrate.py downgrade
```

**List migration status:**
```bash
python migrate.py list
```

---

## My Implementation

### Database Schema

**Products & Clients** (Seed Data - 5 sample clients and 8 sample products included)
```
products: id, name, price
clients: id, name, address, company_registration_no
```

**Invoices** (Generated with auto-incrementing invoice numbers: INV-001, INV-002, etc.)
```
invoices: id, invoice_no, issue_date, due_date, client_id, address, tax, total
invoice_items: id, invoice_id, product_id, quantity, unit_price, subtotal
```

### API Endpoints

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/invoices` | POST | Create a new invoice | Full invoice details (INV-001, etc.) |
| `/invoices` | GET | List all invoices | Array of invoice summaries (without items) |
| `/invoices/{id}` | GET | Get invoice details | Complete invoice with all items |
| `/invoices/{id}` | DELETE | Delete an invoice | 204 No Content |

### Example API Calls

**Create Invoice (POST)**
```bash
curl -X POST http://localhost:8000/invoices \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "issue_date": "2024-02-08",
    "due_date": "2024-03-08",
    "tax": 500,
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 3, "quantity": 1}
    ]
  }'
```

**List All Invoices (GET)**
```bash
curl http://localhost:8000/invoices
```

**Get Invoice Details (GET)**
```bash
curl http://localhost:8000/invoices/1
```

**Delete Invoice (DELETE)**
```bash
curl -X DELETE http://localhost:8000/invoices/1
```
