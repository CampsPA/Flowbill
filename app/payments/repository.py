# Read only atabase queries
# CRUD operations are handled by the Billing Cycly Runner for this application
# Here we have two feth functions - nthing more



from app.payments.model import PaymentAttempt
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging

logger = logging.getLogger("app.payments.repository")

# Create a function to fetch all payment attempts for an invoice
def fetch_all_payment_attempts(db : Session, invoice_id : int):
    # Query all payment attempts by invoice id in desceding orded
    # Note that I use PaymentAttempt.invoice_id == invoice_id since I have not fetched 
    # an invoice first, If I fetch an invoice the I have an invoice object and then
    # I can use invoice_id instead
    payment_attempts = db.execute(select(PaymentAttempt).where(PaymentAttempt.invoice_id == invoice_id).order_by(PaymentAttempt.attempted_at.desc())).scalars().all()    
    return payment_attempts



# Create a function to fetch a single payment attempt by ID for a given invoice
# it also needs to fetche the attempt by Id
def fetch_payment_attempt(db : Session, invoice_id : int, attempt_id : int):
    payment_attempt = db.execute(select(PaymentAttempt).where(PaymentAttempt.invoice_id == invoice_id).where(PaymentAttempt.id == attempt_id)).scalar_one_or_none()

    if not payment_attempt:
        logger.info(f"No payment attempt found with attempt_id {attempt_id} for invoice_id {invoice_id}.")
        logger.info(f"Payment attempt with attempt_id {attempt_id} for invoice_id {invoice_id} successfully retrieved.")
    
    return payment_attempt