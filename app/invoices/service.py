# Here we enforce business rules and raises errors before delegating database 
# operations to the repository.

from app.invoices import repository # this imports all functions from repository.py
from app.invoices.schemas import InvoiceCreate, InvoiceUpdate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import logging
from app.core.enums import InvoiceStatus
# Check for create_invoice
from app.customers import repository as customers_repository # existing customer
from app.subscriptions import repository as subscriptions_repository # existing subscription

logger = logging.getLogger("app.invoices.service")

# Create invoice
def create_invoice(db : Session, invoice : InvoiceCreate):
    # verify existing customer
    existing_customer = customers_repository.get_customer_by_id(db, invoice.customer_id)

    if existing_customer is None:
        logger.info(f"Customer with {invoice.customer_id} does not exist.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer not found")
    
    # Verify existing subscription
    existing_subscription = subscriptions_repository.get_subscription_by_id(db, invoice.subscription_id)

    if existing_subscription is None:
        logger.info(f"Subscription with {invoice.subscription_id} does not exist.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subscription not found")
    
    ## Activate invoice
    invoice_status = InvoiceStatus.OPEN

    # Call repository
    return repository.create_invoice(db, invoice, invoice_status) # these values are the arguments of create_invoice in repository

# Get invoice by Id
def get_invoice_by_id(db : Session, invoice_id : int):
    return repository.get_invoice_by_id(db, invoice_id)


# Get all invoices (needs db and customer_id)
def get_all_invoices(db : Session, customer_id : int):
    return repository.get_all_invoices(db, customer_id)


# Get invoices by subscription
def get_invoices_by_subscription(db : Session, subscription_id : int):
    return repository.get_invoices_by_subscription(db, subscription_id)

# Update invoice
def update_invoice(db : Session, invoice_id : int, invoice_update : InvoiceUpdate):
    invoice =  repository.get_invoice_by_id(db, invoice_id)

    if invoice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found.")
    return repository.update_invoice(db, invoice_id, invoice_update)


