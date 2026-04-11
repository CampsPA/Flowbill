# This is a job - a function that gets called on a svhedule by APScheduler

'''Finish steps 20 and 21 before finishing here'''

from app.database import SessionLocal, get_db
from app.subscriptions.model import Subscription
from app.invoices.model import Invoice
from app.payments.model import PaymentAttempt
from app.plans.model import Plan
from app.core.enums import SubscriptionStatus, InvoiceStatus, PaymentAttemptStatus 
from app.subscriptions import service
from datetime import datetime, timezone, timedelta
import stripe
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session


logger = logging.getLogger("app.billing.cycle_runner")

# Query subscription
# status == active
# current_period_end <= now
# cancel_at_perio_end == False => if True, cancel instead of charge
def run_billing_cycle():
    db = SessionLocal()
    try:
        subscriptions = db.execute(select(Subscription).where(Subscription.status == SubscriptionStatus.ACTIVE).where(Subscription.current_period_end <= datetime.now(timezone.utc)).where(Subscription.cancel_at_period_end == False)).scalars().all()

        # Create invoice
        for subscription in subscriptions:
            # Fetch the plan price
            plan_price = db.execute(select(Plan).where(Plan.id == subscription.plan_id)).scalar_one_or_none()
            # Create the invoice
            new_invoice = Invoice(subscription_id = subscription.id,customer_id = subscription.customer_id,
                                amount_cents = plan_price.price_cents,currency = 'usd',
                                due_date = datetime.now(timezone.utc) + timedelta(days=30),
                                status = InvoiceStatus.OPEN)

            # Attempt payment - if succeed mark invoice as paid
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=new_invoice.amount_cents,
                    currency="usd",
                    customer = "placeholder_stripe_customer_id",
                    payment_method= "place_holder_customer_id",
                    off_session= True,
                    confirm= True)
                # Log payment processed message
                logger.info(f"Payment successful: {payment_intent.id}")
            except stripe.error.CardError as e:
            # Handle failed off-session payments (e.g., authentication required)
                err = e.error
                if err.code == 'authentication_required':
                # Bring the customer back "on-session" to complete authentication
                    logger.info(f"Authentication required for PaymentIntent: {err.payment_intent.id}")

            db.add(new_invoice)
            db.refresh()
    finally:
        db.close()

    
              
# Advance subscription period (new current period starts,
# current period ends


# If payment fails, mark invoice as open,
# hand off to dunning engine to schedule retries


# log failure