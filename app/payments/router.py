# defines 2 HTTP endpoints wired to the queries in repository.py
# I decide to implement custom error handling here since there is no
# service layer in this folder

from fastapi import Depends, APIRouter, Request
from app.payments.schemas import PaymentAttemptResponse
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
import logging
from app.payments import repository
# Custom exceptions
from app.core.exceptions import ResourceNotFound
from app.limiter import limiter


# Get a logger instance
logger = logging.getLogger("app.payments.router")

# Instantiate a router
router = APIRouter(tags=['Payments'])

# Create an endpoint to return all payment attempts for a given invoice
@router.get('/invoice/{invoice_id}', response_model=list[PaymentAttemptResponse])
@limiter.limit("5/minute")
def get_all_payment_attempts(request: Request, invoice_id : int, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return repository.fetch_all_payment_attempts(db, invoice_id)

# Create an endpoint to return a single payment attempt by ID, given an invoice
@router.get('/invoice/{invoice_id}/attempts/{attempt_id}', response_model=PaymentAttemptResponse)
@limiter.limit("5/minute")
def get_payment_attempt(request: Request, invoice_id: int, attempt_id : int, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    payment_attempt = repository.fetch_payment_attempt(db, invoice_id,attempt_id)

    if payment_attempt is None:
        logger.info(f"Payment attempt with attempt id {attempt_id} for invoice with invoice id {invoice_id} not found.")
        raise ResourceNotFound("Payment attempt", attempt_id)

    return payment_attempt
