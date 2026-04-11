# Here we perform the actual CRUD operations against the database. 
# No business rules, no HTTP errors, just database in and database out.

from app.subscriptions.schemas import SubscriptionCreate, SubscriptionUpdate
from app.core.enums import SubscriptionStatus
from app.subscriptions.model import Subscription
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging
from datetime import datetime, timezone

logger = logging.getLogger("app.subscriptions.repository")


# Create a subscription
# This will receive the interval calculation performed by service.py
# No need to explicitly pass customer_id and plan_id because they are inside SubscriptionCreate
# plan_id, current_period_start, current_period_end come from the function parameters therfore don't use subscription.paramenter
def create_subscription(db : Session, subscription : SubscriptionCreate, status : SubscriptionStatus, current_period_start: datetime, current_period_end : datetime):
    new_subscription = Subscription(customer_id = subscription.customer_id, 
                                    plan_id = subscription.plan_id, status = status,
                                    current_period_start = current_period_start,
                                    current_period_end = current_period_end)
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    logger.info(f"Subscription with id {new_subscription.id} successfully created.")
    return new_subscription


# Get subscription by ID
def get_subscription_by_id(db : Session, subscription_id : int):
    subscription = db.execute(select(Subscription).where(Subscription.id == subscription_id)).scalar_one_or_none()

    if subscription is None:
        logger.info(f"No subscription found with id {subscription_id}.")
        return None
    else:
        logger.info(f"Subscription with subscription_id {subscription_id} successfully retrieved.")
    return subscription


# Get all subscriptions (needs db and customer_id)
def get_all_subscriptions(db : Session, customer_id : int):
    # Here we make sure that customer_id matches the customer_id inside Subscription model
    subscriptions = db.execute(select(Subscription).where(Subscription.customer_id == customer_id)).scalars().all()
    return subscriptions



# Update subscription
def update_subscription(db : Session, subscription_id : int, subscription_update : SubscriptionUpdate):
    subscription = db.execute(select(Subscription).where(Subscription.id == subscription_id)).scalar_one_or_none()

    if not subscription:
        logger.info("Subscription not found")
        return None

    #  Extract only set fields
    subscription_update = subscription_update.model_dump(exclude_unset=True)
    
    #  Apply changes
    for key, value in subscription_update.items():
        setattr(subscription, key, value)
    

    db.commit()
    db.refresh(subscription)
    return subscription


# Cancel subscription - note that here we actually cancel the subscription 
# instead of deactivating it
def cancel_subscription(db : Session, subscription_id : int):
    subscription = db.execute(select(Subscription).where(Subscription.id == subscription_id)).scalar_one_or_none()

    if not subscription:
        logger.info("Subscription not found")
        return None
    

    # Cancel Subscription
    subscription.status = SubscriptionStatus.CANCELLED
    subscription.cancelled_at = datetime.now(timezone.utc)
    logger.info(f"Subscription with id {subscription_id} successfully cancelled.")

    db.commit()
    db.refresh(subscription)
    return subscription
