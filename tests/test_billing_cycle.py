# start docker -> run -> python -m pytest tests/test_billing_cycle.py
# This test proves the scheduled billing job creates invoices correctly, advances
#subscription periods, and handles Stripe failures without data corruption

from app.customers.model import Customer
from app.plans.model import Plan
from app.core.enums import PlanInterval, InvoiceStatus
from app.subscriptions.model import Subscription
from app.core.enums import SubscriptionStatus
from datetime import datetime , timezone, timedelta
# Mock tests
from unittest.mock import patch, MagicMock
from app.billing.cycle_runner import run_billing_cycle
from sqlalchemy import select
from app.invoices.model import Invoice 
from app.core.enums import InvoiceStatus, PaymentAttemptStatus
from app.payments.model import PaymentAttempt
import stripe


# Create the fields for the test database


# Happy path test for stripe success (test 1)
def test_stripe_success(db_session):
    # Create customer
    customer = Customer(email = "customer@mail.com", name = "Joe Doe")
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

    # # Save subscription.id as a plain integer before the mock block.
    # Once run_billing_cycle() runs, SQLAlchemy may detach the subscription
    # object from the session making subscription.id inaccessible.
    # A plain integer variable is never affected by session state.
    # Used to query subscriptions only
    subscription_id = subscription.id


    # Save the end of current period so that we can use in the assertion
    original_period_end = subscription.current_period_end


    # Mock Stripe call to call run_billing_cycle()
    with patch("app.billing.cycle_runner.SessionLocal") as mock_session:
        mock_session.return_value = db_session
        with patch("app.billing.cycle_runner.stripe.PaymentIntent.create") as mock_pi:
            mock_pi.return_value = MagicMock(id='pi_test_123')
            # The value id='pi_test_123' is an object returned by mock, it is an arbitrary value that resambles a real
            # Stripe payment ID intent, this format always starts with pi_ and its followed by a ramdom alphanumeric string
            # So for a successful paymment we always return mock_pi.return_value
            run_billing_cycle()


     # Assertions

     # Look up the data models to determined wchich id to use for querying
     # Determine the id by asking yourself which one is the most unique identifier -
     # for example, if you have customer_id and subscription_id the subscription_id
     # is the most unique identifier becuse it is most likely to be tied to an invoice 
     # rather than a customer_id that can have multiple subscriptions and each has its own
     # invoice.
    
    # Query Invoice and assert an invoice was created with status = PAID
    invoice = db_session.execute(select(Invoice).where(Invoice.subscription_id == subscription_id)).scalar_one_or_none()
    assert invoice.status == InvoiceStatus.PAID


    # Query payment_attempt and assert a PaymentAttempt was logged with status SUCCEEDED 
    payment_attempt = db_session.execute(select(PaymentAttempt).where(PaymentAttempt.invoice_id == invoice.id)).scalar_one_or_none()
    assert payment_attempt.status == PaymentAttemptStatus.SUCCEEDED


    # Re-query the subscription form the database so sqlalchemy does not lose track of
    # the original object reference - save it as updated_subscription
    updated_subscription = db_session.execute(select(Subscription).where(Subscription.id == subscription_id)).scalar_one_or_none()

    # Assert the current period now is what the end period was
    assert updated_subscription.current_period_start == original_period_end

    # Assert subscription's current_period_end has advanced by 30 or 365 days depending on interval
    assert updated_subscription.current_period_end > original_period_end


# Test for Stripe failure, CardError (test 2)


# Tests are independent, recreate the fields 
def test_stripe_failure(db_session):
    # Create a customer
    customer = Customer(name = "Paul", email = "user_email@exaamoe.com")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)


    # Create a plan
    plan = Plan(name="Intermediate", price_cents=300, interval=PlanInterval.MONTHLY, trial_days=None, features=None)
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)

    # Create a subscription
    subscription = Subscription(customer_id = customer.id, plan_id = plan.id, status = SubscriptionStatus.ACTIVE, current_period_start = datetime.now(timezone.utc) - timedelta(days=30), current_period_end = datetime.now(timezone.utc) - timedelta(days=1), cancel_at_period_end = False )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)


    # # Save subscription.id as a plain integer before the mock block.
    # Once run_billing_cycle() runs, SQLAlchemy may detach the subscription
    # object from the session making subscription.id inaccessible.
    # A plain integer variable is never affected by session state.
    # Used to query subscriptions only
    subscription_id = subscription.id


    # Save the end of current period so that we can use in the assertion
    original_period_end = subscription.current_period_end


    # Mock Stripe call to call run_billing_cycle()
    with patch("app.billing.cycle_runner.SessionLocal") as mock_session:
        mock_session.return_value = db_session
        with patch("app.billing.cycle_runner.stripe.PaymentIntent.create") as mock_pi:
            mock_pi.side_effect = stripe.error.CardError(message = "Your card declined", param= "card", code= "card_declined")
            # since this mocks a failed paymenyt attempt we use side_effect instead of returning a return_value,
            # with side_effect we pass a stripe.error and the type of error with its required arguments
            # use https://github.com/stripe/stripe-python/blob/master/stripe/_error.py as the reference for the
            # types of errors and their respective classes
            run_billing_cycle()


    # Assertions

    # Query Invoice and assert an invoice was created with status = OPEN
    invoice = db_session.execute(select(Invoice).where(Invoice.subscription_id == subscription_id)).scalar_one_or_none()
    assert invoice.status == InvoiceStatus.OPEN

    # Query payment_attempt and assert a PaymentAttempt was logged with status FAILED
    payment_attempt = db_session.execute(select(PaymentAttempt).where(PaymentAttempt.invoice_id == invoice.id)).scalar_one_or_none()
    assert payment_attempt.status == PaymentAttemptStatus.FAILED

    # Re-query the subscription form the database so sqlalchemy 
    # does not lose track of
    # the original object reference - save it as updated_subscription
    updated_subscription = db_session.execute(select(Subscription).where(Subscription.id == subscription_id)).scalar_one_or_none()
    

    # Assert the PaymentAttempt has a failure_reason that is not None
    assert payment_attempt.failure_reason is not None

    # Assert the subscription period was NOT advanced — billing failed, nothing should change
    assert updated_subscription.current_period_end == original_period_end


# Test Duplicate invoice guard (Test 3)

# Create a subscription with current_period_end in the past (expired)
def test_duplicate_invoice(db_session):

    # Create a customer
    customer = Customer(name = "Paul", email = "user_email@exaamoe.com")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)


    # Create a plan
    plan = Plan(name="Intermediate", price_cents=300, interval=PlanInterval.MONTHLY, trial_days=None, features=None)
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)


    subscription = Subscription(customer_id = customer.id, plan_id = plan.id, status = SubscriptionStatus.ACTIVE, current_period_start = datetime.now(timezone.utc) - timedelta(days=30), current_period_end = datetime.now(timezone.utc) - timedelta(days=1), cancel_at_period_end = False )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)

    # Create an invoice with status as OPEN
    invoice = Invoice(subscription_id = subscription.id, customer_id = customer.id,  status =InvoiceStatus.OPEN,amount_cents=5000, currency ='usd',due_date= datetime.now(timezone.utc) + timedelta(days=30))
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)

    # # Save subscription.id as a plain integer before the mock block.
    # Once run_billing_cycle() runs, SQLAlchemy may detach the subscription
    # object from the session making subscription.id inaccessible.
    # A plain integer variable is never affected by session state.
    # Used to query subscriptions only
    subscription_id = subscription.id


    # Mock invoice creatoion
    # Mock Stripe call to call run_billing_cycle()
    with patch("app.billing.cycle_runner.SessionLocal") as mock_session:
        mock_session.return_value = db_session
        with patch("app.billing.cycle_runner.stripe.PaymentIntent.create") as mock_pi:
            mock_pi.return_value = MagicMock(id='pi_test_456')
            run_billing_cycle()

    # Query all invoices by subscription_id
    invoices = db_session.execute(select(Invoice).where(Invoice.subscription_id == subscription_id)).scalars().all()

    # Assertions

    # Assert ony one invoice exists - no duplicate created
    assert len(invoices) == 1



# Test cancel_at_period_end skipped (test 4)
# A subscription is skipped if the it is set to cancel at the end of current period

def test_skip_subscription(db_session):
    # Create a customer
    customer = Customer(name = "Paulada", email = "user_email@example.com")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)


    # Create a plan
    plan = Plan(name="Premium", price_cents=500, interval=PlanInterval.MONTHLY, trial_days=None, features=None)
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)

    # Set cancel_at_period_end = True for this test
    subscription = Subscription(customer_id = customer.id, plan_id = plan.id, status = SubscriptionStatus.ACTIVE, current_period_start = datetime.now(timezone.utc) - timedelta(days=30), current_period_end = datetime.now(timezone.utc) - timedelta(days=1), cancel_at_period_end = True )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)


    # # Save subscription.id as a plain integer before the mock block.
    # Once run_billing_cycle() runs, SQLAlchemy may detach the subscription
    # object from the session making subscription.id inaccessible.
    # A plain integer variable is never affected by session state.
    # Used to query subscriptions only
    subscription_id = subscription.id


    # Mock invoice creatoion
    # Mock Stripe call to call run_billing_cycle()
    with patch("app.billing.cycle_runner.SessionLocal") as mock_session:
        mock_session.return_value = db_session
        with patch("app.billing.cycle_runner.stripe.PaymentIntent.create") as mock_pi:
            mock_pi.return_value = MagicMock(id='pi_test_333')
            run_billing_cycle()


    # Query all invoices by subscription_id
    invoices = db_session.execute(select(Invoice).where(Invoice.subscription_id == subscription_id)).scalars().all()

    
    # Assertions

    # Assert no invoice was created for that subscription
    assert len(invoices) == 0





    







    



    




