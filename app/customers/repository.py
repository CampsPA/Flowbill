# Here we perform the actual CRUD operations against the database. 
# No business rules, no HTTP errors, just database in and database out.

from app.customers.schemas import CustomerCreate, CustomerUpdate
from app.customers.model import Customer
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging

logger = logging.getLogger("app.customers.repository")


# Create customer
def create_customer(db : Session, customer: CustomerCreate):
    new_customer = Customer(email= customer.email, name=customer.name)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    logger.info(f"Customer with id {new_customer.id} successfully created.")
    return new_customer

# get customer by id
def get_customer_by_id(db : Session, customer_id : int):
    customer = db.execute(select(Customer).where(Customer.id == customer_id)).scalar_one_or_none() # SQLAlchemy 2.0 query style
    
    if customer is None:
        logger.info(f"No customer found with id {customer_id}.")
        return None
    else:
        logger.info(f"Customer with customer id {customer_id} successfully retrieved.")
    return customer
    


# get customer by email
def get_customer_by_email(db : Session, email : str):
    customer = db.execute(select(Customer).where(Customer.email == email)).scalar_one_or_none() # SQLAlchemy 2.0 query style

    if customer is None:
        logger.info(f"No customer found.")
        return None
    else:
        logger.info("Customer successfully retrieved.")
    return customer


# get all customers
# No id since the administrator performing this action is authenticated
def get_all_customers(db: Session):
    customers = db.execute(select(Customer)).scalars().all()
    logger.info(f"Retrieved all customers.")
    return customers


# update customer
def update_customer(db: Session, customer_id : int, customer_update : CustomerUpdate):
    customer = db.execute(select(Customer).where(Customer.id == customer_id)).scalar_one_or_none() # SQLAlchemy 2.0 query style
    if not customer:
        logger.info("Customer not found")
        return None

    #  Extract only set fields
    customer_update = customer_update.model_dump(exclude_unset=True)
    
    #  Apply changes
    for key, value in customer_update.items():
        setattr(customer, key, value)
    

    db.commit()
    db.refresh(customer)
    return customer


# deactivate (delete) customer
def deactivate_customer(db: Session, customer_id : int):
    customer = db.execute(select(Customer).where(Customer.id == customer_id)).scalar_one_or_none() # SQLAlchemy 2.0 query style

    if not customer:
        logger.info("Customer not found")
        return None
    
    # Deactivate customer - set is_active to false
    customer.is_active = False

    db.commit()
    db.refresh(customer)
    return customer