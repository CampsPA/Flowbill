# Here we enforce business rules and raises errors before delegating database 
# operations to the repository.

from app.subscriptions import repository # this imports all functions from repository.py
from app.subscriptions.schemas import SubscriptionCreate, SubscriptionUpdate
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timezone, timedelta
from app.core.enums import SubscriptionStatus, PlanInterval
# Check for create_subscription
from app.customers import repository as customers_repository # existing customer
from app.plans import repository as plans_repository # existing plan
# Custom exceptions
from app.core.exceptions import ResourceNotFound

logger = logging.getLogger("app.subscriptions.service")

# Create subscription
def create_subscription(db : Session, subscription : SubscriptionCreate, ):
    # Verify customer exists
    existing_customer = customers_repository.get_customer_by_id(db, subscription.customer_id)

    if  existing_customer is None:
        logger.info(f"Customer with {subscription.customer_id} does not exist.")
        raise ResourceNotFound("Customer", subscription.customer_id)
        


    # Verify plan exists
    existing_plan = plans_repository.get_plan_by_id(db, subscription.plan_id)

    if existing_plan is  None:
        logger.info(f"Plan with {subscription.plan_id} does snot exist.")
        raise ResourceNotFound("Plan", subscription.plan_id)
    
    # Calculate period dates
    # Set starting period
    current_period_start = datetime.now(timezone.utc)

    if existing_plan.interval == PlanInterval.MONTHLY:
        current_period_end = current_period_start + timedelta(days=30)
    elif existing_plan.interval == PlanInterval.ANNUAL:
        current_period_end = current_period_start + timedelta(days=365) 

    # Activate subscription
    subscription_status = SubscriptionStatus.ACTIVE
    
    # Call repository
    return repository.create_subscription(db, subscription, subscription_status, current_period_start, current_period_end)


# Get subscription by ID
def get_subscription_by_id(db : Session, subscription_id : int):
    return repository.get_subscription_by_id(db, subscription_id)

# Get all subscriptions (needs db and customer_id)
def get_all_subscriptions(db : Session, customer_id : int):
    return repository.get_all_subscriptions(db, customer_id)


# Update subscription
def update_subscription(db : Session, subscription_id : int, subscription_update : SubscriptionUpdate):
    subscription =  repository.get_subscription_by_id(db, subscription_id)

    if subscription is None:
        raise ResourceNotFound("Subscription", subscription_id)
    return repository.update_subscription(db, subscription_id, subscription_update)


# Cancel subscription - note that here we actually cancel the subscription (DELETE)
def cancel_subscription(db : Session, subscription_id : int):
    subscription = repository.get_subscription_by_id(db, subscription_id)

    if subscription is None:
        raise ResourceNotFound("Subscription", subscription_id)
    return repository.cancel_subscription(db, subscription_id)

