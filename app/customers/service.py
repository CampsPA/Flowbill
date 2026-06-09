# Here we enforce business rules and raises errors before delegating database 
# operations to the repository.

from app.customers import repository # this imports all functions from repository.py
from app.customers.schemas import CustomerCreate, CustomerUpdate
from fastapi import status
from sqlalchemy.orm import Session
import logging
# Custom exceptions
from app.core.exceptions import ResourceNotFound, DuplicateRecord
# Customers hard delete: need subscriptions repo to cancel active subs before deleting
from app.subscriptions import repository as subscriptions_repository
from app.core.enums import SubscriptionStatus
from sqlalchemy import select
from app.subscriptions.model import Subscription


logger = logging.getLogger("app.customers.service")


# Create customer
def create_customer(db : Session, customer: CustomerCreate):
    # Check user email, if user exists raise error, if not create user
    existing_customer = repository.get_customer_by_email(db, customer.email)
    
    if  existing_customer is not None:
        logger.info("Customer with email address already registered.")
        raise DuplicateRecord("Email", customer.email)
    
    return repository.create_customer(db, customer)


# get customer by id
def get_customer_by_id(db : Session, customer_id : int):
    return repository.get_customer_by_id(db, customer_id)


# get customer by email
def get_customer_by_email(db : Session, email : str):
    return repository.get_customer_by_email(db, email)


# get all customers
# No id since the administrator performing this action is authenticated
def get_all_customers(db: Session):
    return repository.get_all_customers(db)


# update customer
def update_customer(db: Session, customer_id : int, customer_update : CustomerUpdate):
    customer = repository.get_customer_by_id(db, customer_id)

    if customer is None:
        raise ResourceNotFound("Customer", customer_id)
    return repository.update_customer(db, customer_id, customer_update)



# deactivate (delete) customer
def deactivate_customer(db: Session, customer_id : int):
    customer = repository.get_customer_by_id(db, customer_id)

    if customer is None:
        raise ResourceNotFound("Customer", customer_id)
    return repository.deactivate_customer(db, customer_id)


# Customers hard delete: cancel all active subscriptions then permanently remove the customer row
def hard_delete_customer(db: Session, customer_id: int):
    # Customers hard delete: verify the customer exists first
    customer = repository.get_customer_by_id(db, customer_id)

    if customer is None:
        # Customers hard delete: raise 404 if customer not found
        raise ResourceNotFound("Customer", customer_id)

    # Customers hard delete: fetch all active subscriptions for this customer
    active_subs = db.execute(
        select(Subscription).where(
            Subscription.customer_id == customer_id,
            Subscription.status == SubscriptionStatus.ACTIVE  # only cancel active ones
        )
    ).scalars().all()

    # Customers hard delete: cancel each active subscription before deleting the customer
    for sub in active_subs:
        subscriptions_repository.cancel_subscription(db, sub.id)

    # Customers hard delete: now permanently delete the customer record
    repository.hard_delete_customer(db, customer_id)
    # Customers hard delete: return None since the row is gone
    return None