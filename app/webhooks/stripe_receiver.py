# A single POST endpoint that Stripe calls when something happens in your Stripe account — 
# a payment succeeds, a payment fails, etc. Stripe hits your URL, you verify it's really from Stripe,
# then you act on it.

from fastapi import APIRouter, Request, HTTPException, Depends
from app.core.stripe_client import stripe
from app.config import settings
from app.invoices import service as invoice_service
from sqlalchemy.orm import Session
from app.database import get_db
import logging


# Get a logger instance
logger = logging.getLogger("app.stripe_receiver.router")


# Instantiate a router
router = APIRouter(tags=['Stripe Receiver'])

# Create the endpoint
@router.post("/", status_code = 200)
async def stripe_webhook(request: Request, db : Session = Depends(get_db)):
    # Retrieve body as raw bites
    raw_body : bytes = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            raw_body, request.headers.get("stripe-signature"), settings.stripe_webhook_secret # secret
        )
    except ValueError:
        # Invalid raw_body
        raise HTTPException(status_code=400, detail= "Invalid payload")
    
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    if event.type == "payment_intent.succeeded": # defines that the type of event is 'succeeded'
        payment_intent = event.data.object # # this is the actual Stripe object that triggered the event, that is PaymentIntent
        invoice_id = payment_intent.metadata.get("invoice_id") # cycle_runner.py stored the invoice_id in the PaymentIntent metadata when the charge was created. Here we read it back to know which invoice to update.

        # Update invoice to PAID
        invoice_service.mark_invoice_paid(db, invoice_id)

    elif event.type == "payment_intent.payment_failed":
        payment_intent = event.data.object
        invoice_id = payment_intent.metadata.get("invoice_id")

        # Update invoice to OPEN
        invoice_service.mark_invoice_open(db, invoice_id)
        
        
    logger.info(f"Stripe event received: {event.type}")
    return {"status": "ok"}
        