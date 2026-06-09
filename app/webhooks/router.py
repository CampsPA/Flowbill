# defines HTTP endpoints and delegates to the service layer

from fastapi import Depends, APIRouter, HTTPException  # C4: added HTTPException for endpoint lookup guard
from app.webhooks.schemas import WebhookEndpointCreate, WebhookEndpointResponse, WebhookEndpointUpdate, WebhookDeliverRequest, WebhookEndpointCreateResponse
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
import logging
from app.webhooks import service
# from ..limiter import limiter - it will be created at phase 6

# Get a logger instance
logger = logging.getLogger("app.webhooks.router")

# Instantiate a router
router = APIRouter(tags=['Webhooks']) 


# Create webhook endpoint
@router.post('/', response_model=WebhookEndpointCreateResponse)
#@limiter.limit("5/minute")
def create_webhook_endpoint(endpoint_data : WebhookEndpointCreate,  db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.create_webhook_endpoint(db, endpoint_data, current_user.id)


# Get webhook by id
@router.get('/{endpoint_id}', response_model= WebhookEndpointResponse)
#@limiter.limit("5/minute")
def get_webhook_endpoint_by_id(endpoint_id : int, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.get_webhook_endpoint_by_id(db, endpoint_id, current_user.id)


# Get all webhook endpoints ( by customer)
@router.get('/', response_model=list[WebhookEndpointResponse])
#@limiter.limit("5/minute")
def get_all_webhook_endpoints( db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.get_all_webhook_endpoints(db, current_user.id)


# Update webhook endpoint
@router.patch('/{endpoint_id}', response_model=WebhookEndpointResponse)
#@limiter.limit("5/minute")
def update_webhook_endpoint(endpoint_id : int, endpoint_update : WebhookEndpointUpdate, db : Session = Depends(get_db),  current_user = Depends(get_current_user)):
    return service.update_webhook_endpoint(db, current_user.id, endpoint_id, endpoint_update)

    
# Decativate webhook endpoint
@router.delete('/{endpoint_id}', response_model=WebhookEndpointResponse)
#@limiter.limit("5/minute")
def deactivate_webhook_endpoint(endpoint_id : int, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.deactivate_webhook_endpoint(db, endpoint_id, current_user.id)


# Deliver webhook
# event_type and payload need to come from the request body,
# we need to create a schema for that
@router.post('/{endpoint_id}/deliver', status_code= 200)
#@limiter.limit("5/minute")
def deliver_webhook_endpoint(endpoint_id : int, deliver_request : WebhookDeliverRequest, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    # C4: look up the endpoint first to get its customer_id instead of blindly using current_user.id
    endpoint = service.get_webhook_endpoint_by_id(db, endpoint_id, current_user.id)
    if endpoint is None:
        # C4: guard — return 404 if endpoint not found for this user
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    # C4: use endpoint.customer_id so the delivery targets the right customer's endpoints
    return service.deliver_webhook(db, endpoint.customer_id, deliver_request.event_type , deliver_request.payload)


