# Here we enforce business rules and raises errors before delegating database 
# operations to the repository.

from app.customers import repository # this imports all functions from repository.py
from app.customers.schemas import CustomerCreate, CustomerUpdate
from fastapi import status
from sqlalchemy.orm import Session
import logging
# Custom exceptions
from app.core.exceptions import ResourceNotFound, DuplicateRecord


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