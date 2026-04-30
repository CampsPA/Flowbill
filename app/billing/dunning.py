# Dunning is the process of recovering failed payments. In a subscription billing engine 
# when a charge fails you don't just give up — you retry the charge multiple times over several 
# days before cancelling the subscription.

from app.database import SessionLocal
from app.subscriptions.model import Subscription
from app.invoices.model import Invoice
from app.payments.model import PaymentAttempt
from app.plans.model import Plan
from app.core.enums import SubscriptionStatus, InvoiceStatus, PaymentAttemptStatus, PlanInterval
from datetime import datetime, timezone, timedelta
import stripe
import logging
from sqlalchemy import select
from app.customers.model import Customer
from app.auth.model import User
from app.line_items.model import LineItem
from app.webhooks.model import WebhookEndpoint, WebhookDelivery
from app.core import stripe_client



logger = logging.getLogger("app.billing.dunning")

# Define the number of retries (Charge attempts)
# Retry 1 day after first failed charge, then 3 days after that, if it still fails repeat retries for 7 days
# Afet 7 days invoice becomes INCOLLECTIBLE and subscription PAST DUE
RETRY_SCHEDULE_DAYS = [1, 3, 7]

# Maximun number of retries 
MAX_RETRIES = len(RETRY_SCHEDULE_DAYS)


# Create the function to run the dunning 
def run_dunning():
    # Create a database session
    db = SessionLocal()
    try:
        # Query invoices
        overdue_invoices = db.execute(select(Invoice).where(Invoice.status == InvoiceStatus.OPEN)).scalars().all()
       
        for invoice in overdue_invoices:
            # Fetch all payment attempts for the current invoice
            failed_attempts = db.execute(select(PaymentAttempt).where(PaymentAttempt.invoice_id == invoice.id).where(PaymentAttempt.status == PaymentAttemptStatus.FAILED)).scalars().all()
            # Check for failed attemps, if there are no invoices with failed attempts for collection, continue...
            if not failed_attempts:
                continue

            # If there are invoices with failed attemps ,check if failad attemps is greater than max retries, if so mark invoice as UNCOLLECTIBLE
            if len(failed_attempts) > MAX_RETRIES:

                # Mark invoice as uncollectible
                invoice.status = InvoiceStatus.UNCOLLECTIBLE

                
                # Query subscriptions
                subscription = db.execute(select(Subscription).where(Subscription.id == invoice.subscription_id)).scalar_one_or_none()
                
                # Mark subscription as past due
                subscription.status = SubscriptionStatus.PAST_DUE

                # Save to db
                db.commit()
                db.refresh(invoice)
                
                db.refresh(subscription)

                continue

            # First failed attempt date
            first_failed_at = failed_attempts[0].attempted_at
            # How many days to wait until next retry
            days_to_wait = RETRY_SCHEDULE_DAYS[len(failed_attempts) - 1]
            # Next retry date
            next_retry_date = first_failed_at + timedelta(days=days_to_wait)

            # Check if we are still in the retry date window, continue attempting to charge
            if datetime.now(timezone.utc) < next_retry_date:
                continue

            # Attempt charge
            try:
                # Fetch suscription to use in the charge attempt using the invoive id
                subscription = db.execute(select(Subscription).where(Subscription.id == invoice.subscription_id)).scalar_one_or_none()
                
                
                payment_intent = stripe.PaymentIntent.create(
                    amount=invoice.amount_cents,
                    currency="usd",
                    customer = "placeholder_stripe_customer_id",
                    payment_method= "place_holder_customer_id",
                    off_session= True,
                    confirm= True)
                # Log payment processed message
                logger.info(f"Payment successful: {payment_intent.id}")


                # Payment success handling (sucess)
                invoice.status = InvoiceStatus.PAID


                # Record payment date
                invoice.paid_at = datetime.now(timezone.utc)

                # Fetch the plan price
                plan_price = db.execute(select(Plan).where(Plan.id == subscription.plan_id)).scalar_one_or_none()

                # Set begining period for current subscription
                # The old period becomes the new start, the calculate the new end
                # here I update the acutual subscription record, I dont create a new one
                subscription.current_period_start = subscription.current_period_end

                # Advance subscription period
                if plan_price.interval == PlanInterval.MONTHLY:
                    subscription.current_period_end = subscription.current_period_start + timedelta(days=30)
                elif plan_price.interval == PlanInterval.ANNUAL:
                    subscription.current_period_end = subscription.current_period_start + timedelta(days=365) 
                
                # Log the payment attempt 
                new_payment = PaymentAttempt(invoice_id = invoice.id,
                                attempted_at = datetime.now(timezone.utc),
                                status = PaymentAttemptStatus.SUCCEEDED,
                                stripe_payment_intent_id = payment_intent.id,
                                failure_reason = None)
                
                # Save all changes
                db.add(new_payment)
                db.commit()
                db.refresh(invoice) # updates changes in the new invoice
                db.refresh(subscription) # updates changes in the subscription

                # Log successfull payment
                logger.info(f"Payment attempt logged for invoice {invoice.id}")

            # Payment failure handling
            except (stripe.error.CardError, stripe.error.InvalidRequestError) as e:

                # Set the status as open
                invoice.status = InvoiceStatus.OPEN

                # Log the payment attempt (failure)
                new_payment = PaymentAttempt(invoice_id = invoice.id,
                                attempted_at = datetime.now(timezone.utc),
                                status = PaymentAttemptStatus.FAILED,
                                stripe_payment_intent_id = "failed_" + str(invoice.id),
                                failure_reason = str(e))
                
                # Save all changes
                db.add(new_payment)
                db.commit()

                # Log failed payment
                logger.info(f"Payment failed for invoice {invoice.id}: {str(e)}")

                
    finally:
        db.close()

            

                

            
