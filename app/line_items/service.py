# enforces business rules and raises errors before delegating to the repository

from app.line_items import repository # this imports all functions from repository.py
from app.line_items.schemas import LineItemCreate, LineItemUpdate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import logging
# Check for existing invoice
from app.invoices import repository as invoices_repository 


logger = logging.getLogger("app.line_items.service")

# Rule: Here the functions are the same as in repository.py

# Create line item
def create_line_item(db : Session, line_item : LineItemCreate):
    # Check if invoice exists
    existing_invoice = invoices_repository.get_invoice_by_id(db, line_item.invoice_id)

    if existing_invoice is None:
        logger.info(f"Invoice with {line_item.invoice_id} does not exist.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invoice not found")
    
    # Call repository
    return repository.create_line_item(db, line_item) # these values are the arguments of create_line_item in repository


# Get line item by id
def get_line_item_by_id(db : Session, line_item_id : int):
    return repository.get_line_item_by_id(db, line_item_id)


# Get line items by invoice (filter by invoice_id)
def get_line_item_by_invoice(db : Session, invoice_id : int):
    return repository.get_line_item_by_invoice(db, invoice_id)


# Update line item
def update_line_item(db : Session, line_item_id : int, line_item_update : LineItemUpdate):
    line_item = repository.get_line_item_by_id(db, line_item_id)

    if line_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line item not found.")
    return repository.update_line_item(db, line_item_id, line_item_update)
