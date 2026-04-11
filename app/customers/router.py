# Hare we define the HTTP endpoints, handles requests and responses, 
# and delegates to the service layer.

from fastapi import Depends, APIRouter
from app.customers.schemas import CustomerCreate, CustomerResponse, CustomerUpdate
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
import logging
from app.customers import service
# from ..limiter import limiter - it will be created at phase 6


# Get a logger instance
logger = logging.getLogger("app.customers.router")

# Instantiate a router
router = APIRouter(tags=['Customers']) 

# Create customer endpoint
@router.post('/',response_model=CustomerResponse)
#@limiter.limit("5/minute")
def create_customer(customer_data: CustomerCreate, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.create_customer(db, customer_data)
    

# Get custmomer by id endpoint
@router.get('/{customer_id}', response_model=CustomerResponse)
#@limiter.limit("5/minute")
def get_customer_by_id(customer_id : int, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.get_customer_by_id(db, customer_id)


# Get all customers
@router.get('/', response_model=list[CustomerResponse])
#@limiter.limit("5/minute")
def get_customers(db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.get_all_customers(db)


# Update customers
@router.patch('/{customer_id}', response_model=CustomerResponse)
#@limiter.limit("5/minute")
def update_customer(customer_id : int, customer_update : CustomerUpdate, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.update_customer(db, customer_id, customer_update)


# Deactivate (delete) customers
@router.delete('/{customer_id}', response_model=CustomerResponse)
#@limiter.limit("5/minute")
def deactivate_customer(customer_id : int,  db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.deactivate_customer(db, customer_id)

