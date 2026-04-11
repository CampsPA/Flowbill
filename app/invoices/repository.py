# Here we perform the actual CRUD operations against the database. 
# No business rules, no HTTP errors, just database in and database out.

from app.invoices.schemas import InvoiceCreate, InvoiceUpdate
from app.core.enums import InvoiceStatus
from app.invoices.model import Invoice
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging
from datetime import datetime, timezone

logger = logging.getLogger("app.invoices.repository")

# Create Invoice
def create_invoice(db : Session, invoice : InvoiceCreate, status : InvoiceStatus):
    new_invoice = Invoice(subscription_id = invoice.subscription_id, customer_id = invoice.customer_id,
                          status = status,
                          amount_cents = invoice.amount_cents, currency = invoice.currency,
                          due_date = invoice.due_date)
    
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    logger.info(f"Invoice with id {new_invoice.id} successfully created.")
    return new_invoice

# Get invoice by Id
def get_invoice_by_id(db : Session, invoice_id : int):
    invoice = db.execute(select(Invoice).where(Invoice.id == invoice_id)).scalar_one_or_none()

    if invoice is None:
        logger.info(f"No invoice found with id {invoice_id}.")
        return None
    else:
        logger.info(f"Invoice with invoice_id {invoice_id} successfully retrieved.")
    return invoice

# Get all invoices (needs db and customer_id)
def get_all_invoices(db : Session, customer_id : int):
    # Here we make sure that customer_id matches the customer_id inside Subscription model
    invoices = db.execute(select(Invoice).where(Invoice.customer_id == customer_id)).scalars().all()
    return invoices

# Get invoices by subscription
def get_invoices_by_subscription(db : Session, subscription_id : int):
    invoices = db.execute(select(Invoice).where(Invoice.subscription_id == subscription_id)).scalars().all()
    return invoices

# Update invoice
def update_invoice(db : Session, invoice_id : int, invoice_update : InvoiceUpdate):
    invoice = db.execute(select(Invoice).where(Invoice.id == invoice_id)).scalar_one_or_none()

    if not invoice:
        logger.info("Invoice not found")
        return None

    #  Extract only set fields
    invoice_update = invoice_update.model_dump(exclude_unset=True)
    
    #  Apply changes
    for key, value in invoice_update.items():
        setattr(invoice, key, value)
    

    db.commit()
    db.refresh(invoice)
    return invoice
 