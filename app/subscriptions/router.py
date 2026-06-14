# defines HTTP endpoints and delegates to the service layer

from fastapi import Depends, APIRouter, Request
from app.subscriptions.schemas import SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
import logging
from app.subscriptions import service
from app.limiter import limiter


# Get a logger instance
logger = logging.getLogger("app.subscriptions.router")

# Instantiate a router
router = APIRouter(tags=['Subscriptions'])

# Create subscription endpoint
@limiter.limit("5/minute")
@router.post('/',response_model=SubscriptionResponse)
def create_subscription(request: Request, subscription_data: SubscriptionCreate, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.create_subscription(db, subscription_data)

# Get subscription by ID
@limiter.limit("5/minute")
@router.get('/{subscription_id}',response_model=SubscriptionResponse)
def get_subscription_by_id(request: Request, subscription_id : int, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.get_subscription_by_id(db, subscription_id)


# Get all subscriptions (needs db and customer_id)
@limiter.limit("5/minute")
@router.get('/', response_model=list[SubscriptionResponse])
def get_subscriptions(request: Request, customer_id : int, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.get_all_subscriptions(db, customer_id)


# Update subscription
@limiter.limit("5/minute")
@router.patch('/{subscription_id}', response_model=SubscriptionResponse)
def update_subscription(request: Request, subscription_id : int, subscription_update : SubscriptionUpdate, db:Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.update_subscription(db, subscription_id, subscription_update)


# Cancel subscription - note that here we actually cancel the subscription (DELETE)
@limiter.limit("5/minute")
@router.delete('/{subscription_id}', response_model=SubscriptionResponse)
def cancel_subscription(request: Request, subscription_id : int, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.cancel_subscription(db, subscription_id)
