# defines HTTP endpoints and delegates to the service layer

from fastapi import Depends, APIRouter, HTTPException, Request  # C4: added HTTPException for endpoint lookup guard
from app.webhooks.schemas import WebhookEndpointCreate, WebhookEndpointResponse, WebhookEndpointUpdate, WebhookDeliverRequest, WebhookEndpointCreateResponse
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
import logging
from app.webhooks import service
from app.limiter import limiter

# Get a logger instance
logger = logging.getLogger("app.webhooks.router")

# Instantiate a router
router = APIRouter(tags=['Webhooks'])


# Create webhook endpoint
@limiter.limit("5/minute")
@router.post('/', response_model=WebhookEndpointCreateResponse)
def create_webhook_endpoint(request: Request, endpoint_data : WebhookEndpointCreate,  db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.create_webhook_endpoint(db, endpoint_data, endpoint_data.customer_id)


# Get webhook by id
@limiter.limit("5/minute")
@router.get('/{endpoint_id}', response_model= WebhookEndpointResponse)
def get_webhook_endpoint_by_id(request: Request, endpoint_id : int, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.get_webhook_endpoint_by_id(db, endpoint_id, current_user.id)


# Get all webhook endpoints ( by customer)
@limiter.limit("5/minute")
@router.get('/', response_model=list[WebhookEndpointResponse])
def get_all_webhook_endpoints(request: Request, customer_id: int, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.get_all_webhook_endpoints(db, customer_id)


# Update webhook endpoint
@limiter.limit("5/minute")
@router.patch('/{endpoint_id}', response_model=WebhookEndpointResponse)
def update_webhook_endpoint(request: Request, endpoint_id : int, endpoint_update : WebhookEndpointUpdate, db : Session = Depends(get_db),  current_user = Depends(get_current_user)):
    return service.update_webhook_endpoint(db, current_user.id, endpoint_id, endpoint_update)


# Decativate webhook endpoint
@limiter.limit("5/minute")
@router.delete('/{endpoint_id}', response_model=WebhookEndpointResponse)
def deactivate_webhook_endpoint(request: Request, endpoint_id : int, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.deactivate_webhook_endpoint(db, endpoint_id, current_user.id)


# Deliver webhook
# event_type and payload need to come from the request body,
# we need to create a schema for that
@limiter.limit("5/minute")
@router.post('/{endpoint_id}/deliver', status_code= 200)
def deliver_webhook_endpoint(request: Request, endpoint_id : int, deliver_request : WebhookDeliverRequest, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    # C4: look up the endpoint first to get its customer_id instead of blindly using current_user.id
    endpoint = service.get_webhook_endpoint_by_id_only(db, endpoint_id)
    if endpoint is None:
        # C4: guard — return 404 if endpoint not found for this user
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    # C4: use endpoint.customer_id so the delivery targets the right customer's endpoints
    return service.deliver_webhook(db, endpoint.customer_id, deliver_request.event_type , deliver_request.payload)
