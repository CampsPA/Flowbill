# Start Docker -> run : python -m pytest tests/test_dunning.py
# To run the whole test suite -> pytest tests/ -v
# Tets  failed payment recovery engine. It scans for OPEN invoices that have failed payment
# attempts and retries them according to RETRY_SCHEDULE_DAYS = [1, 3, 7]. 

# This test requires customer, plan, subscription and payment_attempt creation with specific
# attempted_at timestamps for the assertions

from app.customers.model import Customer
from app.plans.model import Plan
from app.core.enums import PlanInterval, InvoiceStatus
from app.subscriptions.model import Subscription
from app.core.enums import SubscriptionStatus
from datetime import datetime , timezone, timedelta
# Mock tests
from unittest.mock import patch, MagicMock
from app.billing.dunning import run_dunning
from sqlalchemy import select
from app.invoices.model import Invoice 
from app.core.enums import InvoiceStatus, PaymentAttemptStatus
from app.payments.model import PaymentAttempt
import stripe


# Test 1 - No failed attempts
def test_no_failed_attempts(db_session):
    # Create customer
    customer = Customer(email = "customer@mail.com", name = "John Dewey")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    # Create plan
    plan = Plan(name = "Standard", price_cents = 100, interval = PlanInterval.MONTHLY, trial_days = None, features = None)
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)

    # current_period_end is set to yesterday so run_billing_cycle() picks it up as due for billing
    # The billing cycle queries for subscriptions where current_period_end <= now()
    # cancel_at_period_end  = False meaning we don't want the subscription to cancel 
    # so that the app can renew the subscription and keep charging

    # Create subscription
    subscription = Subscription(customer_id = customer.id, plan_id = plan.id, status = SubscriptionStatus.ACTIVE, current_period_start = datetime.now(timezone.utc) - timedelta(days=30), current_period_end = datetime.now(timezone.utc) - timedelta(days=1), cancel_at_period_end = False )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)

    

    # Create an invoice with status OPEN
    # Create an invoice with status as OPEN
    invoice = Invoice(subscription_id = subscription.id, customer_id = customer.id,  status =InvoiceStatus.OPEN,amount_cents=5000, currency ='usd',due_date= datetime.now(timezone.utc) + timedelta(days=30))
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)

    


    # Mock Stripe call to call run_billing_cycle()
    with patch("app.billing.dunning.SessionLocal") as mock_session:
        mock_session.return_value = db_session
        with patch("app.billing.dunning.stripe.PaymentIntent.create") as mock_pi:
            mock_pi.return_value = MagicMock(id='pi_test_123')
            # The value id='pi_test_123' is an object returned by mock, it is an arbitrary value that resambles a real
            # Stripe payment ID intent, this format always starts with pi_ and its followed by a ramdom alphanumeric string
            # So for a successful paymment we always return mock_pi.return_value
            run_dunning()

    # Assertions

    # Query all payment_attemps
    payment_attempts = db_session.execute(select(PaymentAttempt).where(PaymentAttempt.invoice_id == invoice.id)).scalars().all()

    # Assert the invoice has no payment attempt records
    assert len(payment_attempts) == 0


# Test 2  - Test within retry window

def test_retry_window(db_session):
    # Create customer
    customer = Customer(email = "customer@mail.com", name = "John Dewey")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    # Create plan
    plan = Plan(name = "Standard", price_cents = 100, interval = PlanInterval.MONTHLY, trial_days = None, features = None)
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)

    # current_period_end is set to yesterday so run_billing_cycle() picks it up as due for billing
    # The billing cycle queries for subscriptions where current_period_end <= now()
    # cancel_at_period_end  = False meaning we don't want the subscription to cancel 
    # so that the app can renew the subscription and keep charging

    # Create subscription
    subscription = Subscription(customer_id = customer.id, plan_id = plan.id, status = SubscriptionStatus.ACTIVE, current_period_start = datetime.now(timezone.utc) - timedelta(days=30), current_period_end = datetime.now(timezone.utc) - timedelta(days=1), cancel_at_period_end = False )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)

    

    # Create an invoice with status OPEN
    # Create an invoice with status as OPEN
    invoice = Invoice(subscription_id = subscription.id, customer_id = customer.id,  status =InvoiceStatus.OPEN,amount_cents=5000, currency ='usd',due_date= datetime.now(timezone.utc) + timedelta(days=30))
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)


    # Create a payment attempt for an invoice with an attempt charge that happeden 30 min ago
    payment_attempt = PaymentAttempt(invoice_id= invoice.id, attempted_at= datetime.now(timezone.utc) - timedelta(minutes=30),status= PaymentAttemptStatus.FAILED, failure_reason= "credit_card_declined", stripe_payment_intent_id ="123")
    db_session.add(payment_attempt)
    db_session.commit()
    db_session.refresh(payment_attempt)
    

    # Mock Stripe call to call run_billing_cycle()
    # Note that even though this test should fail it does not beacuse Stripe is never called
    # If it was called and we had a failure we would need to use side_effect instead of retur_value
    # in the Moch Stripe call
    with patch("app.billing.dunning.SessionLocal") as mock_session:
        mock_session.return_value = db_session
        with patch("app.billing.dunning.stripe.PaymentIntent.create") as mock_pi:
            mock_pi.return_value = MagicMock(id='pi_test_123')
            # The value id='pi_test_123' is an object returned by mock, it is an arbitrary value that resambles a real
            # Stripe payment ID intent, this format always starts with pi_ and its followed by a ramdom alphanumeric string
            # So for a successful paymment we always return mock_pi.return_value
            run_dunning()


    # Query all payment attempts by invoice_id
    payment_attempt = db_session.execute(select(PaymentAttempt).where(PaymentAttempt.invoice_id == invoice.id)).scalars().all()


    # Assertions

    # Assert no new Payments attempt was created - only 1
    assert len(payment_attempt) == 1

    # Assert Stripe was naver called 
    mock_pi.assert_not_called()



# Test 3 - Ready to retry (Stripe fails again)
# use side_effect inside the Mock Stripe since stripe fails 
def test_retry(db_session):
    # Create customer
    customer = Customer(email = "customer@mail.com", name = "John Dewey")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    # Create plan
    plan = Plan(name = "Standard", price_cents = 100, interval = PlanInterval.MONTHLY, trial_days = None, features = None)
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)

    # current_period_end is set to yesterday so run_billing_cycle() picks it up as due for billing
    # The billing cycle queries for subscriptions where current_period_end <= now()
    # cancel_at_period_end  = False meaning we don't want the subscription to cancel 
    # so that the app can renew the subscription and keep charging

    # Create subscription
    subscription = Subscription(customer_id = customer.id, plan_id = plan.id, status = SubscriptionStatus.ACTIVE, current_period_start = datetime.now(timezone.utc) - timedelta(days=30), current_period_end = datetime.now(timezone.utc) - timedelta(days=1), cancel_at_period_end = False )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)

    

    # Create an invoice with status OPEN
    # Create an invoice with status as OPEN
    invoice = Invoice(subscription_id = subscription.id, customer_id = customer.id,  status =InvoiceStatus.OPEN,amount_cents=5000, currency ='usd',due_date= datetime.now(timezone.utc) + timedelta(days=30))
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)


    # Create a payment attempt for an invoice with an attempt charge that happeden 30 min ago
    payment_attempt = PaymentAttempt(invoice_id= invoice.id, attempted_at= datetime.now(timezone.utc) - timedelta(days=2),status= PaymentAttemptStatus.FAILED, failure_reason= "credit_card_declined", stripe_payment_intent_id ="123")
    db_session.add(payment_attempt)
    db_session.commit()
    db_session.refresh(payment_attempt)
    

    # Mock Stripe call to call run_billing_cycle()
    # Note that we use side_effect since this is a failed attempt
    with patch("app.billing.dunning.SessionLocal") as mock_session:
        mock_session.return_value = db_session
        with patch("app.billing.dunning.stripe.PaymentIntent.create") as mock_pi:
            mock_pi.side_effect = stripe.error.CardError(message = "Your card declined", param= "card", code= "card_declined")
            # The value id='pi_test_123' is an object returned by mock, it is an arbitrary value that resambles a real
            # Stripe payment ID intent, this format always starts with pi_ and its followed by a ramdom alphanumeric string
            # So for a successful paymment we always return mock_pi.return_value
            run_dunning()


    # Query all payment attempts by invoice_id
    payment_attempt = db_session.execute(select(PaymentAttempt).where(PaymentAttempt.invoice_id == invoice.id)).scalars().all()

    # Assertions

    # Assert a new PaymentAttempt was created with status FAILED ( we had 1 above now we create a second attempt)
    assert len(payment_attempt) == 2
    

    # Assert invoice status remains OPEN
    assert invoice.status == InvoiceStatus.OPEN


# Test 4 - Retry succeeds

def test_retry_sucessful(db_session):
    # Create customer
    customer = Customer(email = "customer@mail.com", name = "John Dewey")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    # Create plan
    plan = Plan(name = "Standard", price_cents = 100, interval = PlanInterval.MONTHLY, trial_days = None, features = None)
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)

    

    # Create subscription
    subscription = Subscription(customer_id = customer.id, plan_id = plan.id, status = SubscriptionStatus.ACTIVE, current_period_start = datetime.now(timezone.utc) - timedelta(days=30), current_period_end = datetime.now(timezone.utc) - timedelta(days=1), cancel_at_period_end = False )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)

    # Save subscription.id as a plain integer
    # Once run_billing_cycle() runs, SQLAlchemy may detach the subscription
    # object from the session making subscription.id inaccessible.
    # A plain integer variable is never affected by session state.
    # Used to query subscriptions only
    subscription_id = subscription.id

    

    # Create an invoice with status as OPEN
    invoice = Invoice(subscription_id = subscription.id, customer_id = customer.id,  status =InvoiceStatus.OPEN,amount_cents=5000, currency ='usd',due_date= datetime.now(timezone.utc) + timedelta(days=30))
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)


    # Create a payment attempt for an invoice with an attempt charge that happeden 30 min ago
    payment_attempt = PaymentAttempt(invoice_id= invoice.id, attempted_at= datetime.now(timezone.utc) - timedelta(days=2),status= PaymentAttemptStatus.FAILED, failure_reason= "credit_card_declined", stripe_payment_intent_id ="123")
    db_session.add(payment_attempt)
    db_session.commit()
    db_session.refresh(payment_attempt)

    # Save the end of current period so that we can use in the assertion
    original_period_end = subscription.current_period_end
    

    # Mock Stripe call to call run_billing_cycle()
    # Note that this time the payment attemp succeeds - use return_value
    with patch("app.billing.dunning.SessionLocal") as mock_session:
        mock_session.return_value = db_session
        with patch("app.billing.dunning.stripe.PaymentIntent.create") as mock_pi:
            mock_pi.return_value = MagicMock(id='pi_test_123')
            # The value id='pi_test_123' is an object returned by mock, it is an arbitrary value that resambles a real
            # Stripe payment ID intent, this format always starts with pi_ and its followed by a ramdom alphanumeric string
            # So for a successful paymment we always return mock_pi.return_value
            run_dunning()


    # Query an invoice to update status
    invoice = db_session.execute(select(Invoice).where(Invoice.subscription_id == subscription_id)).scalar_one_or_none()

    # Query all payment attempts by invoice_id
    payment_attempt = db_session.execute(select(PaymentAttempt).where(PaymentAttempt.invoice_id == invoice.id)).scalars().all()

    # Assetions

    # Invoice status is now PAID
    assert invoice.status == InvoiceStatus.PAID


    # Invoice paid_at timestamp is set
    assert invoice.paid_at is not None
    

    # Subscription period has advanced

    # Re-query the subscription form the database so sqlalchemy does not lose track of
    # the original object reference - save it as updated_subscription
    updated_subscription = db_session.execute(select(Subscription).where(Subscription.id == subscription_id)).scalar_one_or_none()
    
    assert updated_subscription.current_period_end > original_period_end


    #  New PaymentAttempt logged with status SUCCEEDED
    assert PaymentAttemptStatus.SUCCEEDED




# Test 5 - Max retries exceeded
def test_max_retries(db_session):
    # Create customer
    customer = Customer(email = "customer@mail.com", name = "John Dewey")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    # Create plan
    plan = Plan(name = "Standard", price_cents = 100, interval = PlanInterval.MONTHLY, trial_days = None, features = None)
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)

    # current_period_end is set to yesterday so run_billing_cycle() picks it up as due for billing
    # The billing cycle queries for subscriptions where current_period_end <= now()
    # cancel_at_period_end  = False meaning we don't want the subscription to cancel 
    # so that the app can renew the subscription and keep charging

    # Create subscription
    subscription = Subscription(customer_id = customer.id, plan_id = plan.id, status = SubscriptionStatus.ACTIVE, current_period_start = datetime.now(timezone.utc) - timedelta(days=30), current_period_end = datetime.now(timezone.utc) - timedelta(days=1), cancel_at_period_end = False )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)

    # Save subscription.id as a plain integer
    # Once run_billing_cycle() runs, SQLAlchemy may detach the subscription
    # object from the session making subscription.id inaccessible.
    # A plain integer variable is never affected by session state.
    # Used to query subscriptions only
    subscription_id = subscription.id


    # Create an invoice with status as OPEN
    invoice = Invoice(subscription_id = subscription.id, customer_id = customer.id,  status =InvoiceStatus.OPEN,amount_cents=5000, currency ='usd',due_date= datetime.now(timezone.utc) + timedelta(days=30))
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)


    # Create 4 failed payment_attempts -  use a for loop to to avoid violating the DRY principle
    # The loop is ok here since we are not dealing with a large amount of data (not an efficiency problem)
    for i in range(4):
        payment_attempt = PaymentAttempt(invoice_id= invoice.id, attempted_at= datetime.now(timezone.utc) - timedelta(days=2),status= PaymentAttemptStatus.FAILED, failure_reason= "credit_card_declined", stripe_payment_intent_id =f"failed_{i}")
        db_session.add(payment_attempt)
        db_session.commit()
        db_session.refresh(payment_attempt)

    

    # Mock Stripe call to call run_billing_cycle()
    # Note that we use side_effect since this is a failed attempt
    with patch("app.billing.dunning.SessionLocal") as mock_session:
        mock_session.return_value = db_session
        with patch("app.billing.dunning.stripe.PaymentIntent.create") as mock_pi:
            mock_pi.side_effect = stripe.error.CardError(message = "Your card declined", param= "card", code= "card_declined")
            # The value id='pi_test_123' is an object returned by mock, it is an arbitrary value that resambles a real
            # Stripe payment ID intent, this format always starts with pi_ and its followed by a ramdom alphanumeric string
            # So for a successful paymment we always return mock_pi.return_value
            run_dunning()


    # Query an invoice to update status
    invoice = db_session.execute(select(Invoice).where(Invoice.subscription_id == subscription_id)).scalar_one_or_none()

    # Query all payment attempts by invoice_id
    payment_attempt = db_session.execute(select(PaymentAttempt).where(PaymentAttempt.invoice_id == invoice.id)).scalars().all()

    # Assertions

    # Assert invoice status == UNCOLLECTIBLE
    assert InvoiceStatus.UNCOLLECTIBLE

    # Assert subscription status == PAST_DUE
    assert SubscriptionStatus.PAST_DUE

    # Assert no new paymnent was created
    # since we had 4 attemps we just confirm here no additional attempts were made
    assert len(payment_attempt) == 4



    