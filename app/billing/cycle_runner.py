# This is a job - a function that gets called on a schedule by APScheduler


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

# Email integration
from app.core.email import send_invoice_email
from app.core.pdf import generate_invoice_pdf
from app.customers import repository as customer_repository
from app.tenant_settings import repository as tenant_settings_repository



logger = logging.getLogger("app.billing.cycle_runner")


def run_billing_cycle():
    # Create a database session
    db = SessionLocal()
    try:
        # Query subscriptions
        subscriptions = db.execute(select(Subscription).where(Subscription.status == SubscriptionStatus.ACTIVE).where(Subscription.current_period_end <= datetime.now(timezone.utc)).where(Subscription.cancel_at_period_end == False)).scalars().all()

        # Create invoice
        for subscription in subscriptions:
            # Fetch the plan price
            plan_price = db.execute(select(Plan).where(Plan.id == subscription.plan_id)).scalar_one_or_none()

            # Add a check to prevent creating duplicate invoices
            invoice_check = db.execute(select(Invoice).where(Invoice.subscription_id == subscription.id).where(Invoice.status == InvoiceStatus.OPEN)).scalars().first()
            
            if invoice_check is not None:
                continue

            # Create the invoice
            new_invoice = Invoice(subscription_id = subscription.id,customer_id = subscription.customer_id,
                                amount_cents = plan_price.price_cents,currency = 'usd',
                                due_date = datetime.now(timezone.utc) + timedelta(days=30),
                                status = InvoiceStatus.OPEN)
            # Add invoice
            db.add(new_invoice)
            db.commit()
            db.refresh(new_invoice)


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


                # Payment success handling (sucess)
                new_invoice.status = InvoiceStatus.PAID



                # Generate PDF bytes -> fetch customer by id, tenants_settings by customer_id, use new_invoice instead of invoice

                try:
                    customer = customer_repository.get_customer_by_id(db,new_invoice.customer_id)
                    tenant_settings = tenant_settings_repository.get_by_customer_id(db, new_invoice.customer_id)
                    pdf_bytes = generate_invoice_pdf(new_invoice, customer, tenant_settings)

                    send_invoice_email(customer, new_invoice, pdf_bytes)

                except Exception as e:
                    logger.error(f'Email failed for invoice {new_invoice.id}: {e}')



                # Record payment date
                new_invoice.paid_at = datetime.now(timezone.utc)

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
                new_payment = PaymentAttempt(invoice_id = new_invoice.id,
                                attempted_at = datetime.now(timezone.utc),
                                status = PaymentAttemptStatus.SUCCEEDED,
                                stripe_payment_intent_id = payment_intent.id,
                                failure_reason = None)
                
                # Save all changes
                db.add(new_payment)
                db.commit()
                db.refresh(new_invoice) # updates changes in the new invoice
                db.refresh(subscription) # updates changes in the subscription

                # Log successfull payment
                logger.info(f"Payment attempt logged for invoice {new_invoice.id}")
                
            except (stripe.error.CardError, stripe.error.InvalidRequestError) as e:
                # Payment failure handling
                new_invoice.status = InvoiceStatus.OPEN

                # Log the payment attempt 
                new_payment = PaymentAttempt(invoice_id = new_invoice.id,
                                attempted_at = datetime.now(timezone.utc),
                                status = PaymentAttemptStatus.FAILED,
                                stripe_payment_intent_id = "failed_" + str(new_invoice.id),
                                failure_reason = str(e))
                
                # Save all changes
                db.add(new_payment)
                db.commit()

                # Log failed payment
                logger.info(f"Payment failed for invoice {new_invoice.id}: {str(e)}")

                
    finally:
        db.close()

    
              
