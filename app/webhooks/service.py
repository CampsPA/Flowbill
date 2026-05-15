# Here we enforce business rules and raises errors before delegating database 
# operations to the repository

# Mimimcs the functions on repository.py with w additional functions:
# 1- create_webhook_endpoint — before creating, check if the customer already has an active endpoint 
# registered for that same URL. You don't want duplicate registrations.

# 2- deliver_webhook -> This is the outbound delivery engine. It:

# Finds all active endpoints subscribed to a given event
# Sends an HTTP POST to each URL using httpx
# Logs the delivery result using create_webhook_delivery

 # this imports all functions from repository.py
from app.webhooks.schemas import WebhookEndpointCreate, WebhookEndpointUpdate
from sqlalchemy.orm import Session
import logging
from app.webhooks import repository as webhook_repository
from app.core.enums import WebhookDeliveryStatus
from datetime import datetime
from sqlalchemy import select
from app.webhooks.model import WebhookEndpoint
import httpx
# Custom exceptions
from app.core.exceptions import DuplicateRecord


logger = logging.getLogger("app.webhooks.service")


# Create webhook endpoint
def create_webhook_endpoint(db : Session, endpoint : WebhookEndpointCreate, customer_id : int):
    # Check if the customer already has a registered URL (avoid duplication)
    existing_url = webhook_repository.get_webhook_endpoint_by_url(db, url = endpoint.url, customer_id = customer_id) # here I call url = endpoint.url bacuse I'm looking to see if the url exists

    if  existing_url is not None:
        logger.info("Endpoint with this url is already registered.")
        raise DuplicateRecord("url", endpoint.url)
        
    return webhook_repository.create_webhook_endpoint(db, endpoint, customer_id) # here I call endpoint beacuse I'm creating the endpoint


# Create webhook endpoint by id
def get_webhook_endpoint_by_id(db : Session, endpoint_id : int, customer_id : int):
    return webhook_repository.get_webhook_endpoint_by_id(db, endpoint_id, customer_id)




# Get all webhook endpoints ( by customer)
def get_all_webhook_endpoints(db : Session, customer_id : int):
    return webhook_repository.get_all_webhook_endpoints(db, customer_id)



# Update webhook endpoint
def update_webhook_endpoint(db : Session,customer_id : int, endpoint_id : int, endpoint_update : WebhookEndpointUpdate):
    return webhook_repository.update_webhook_endpoint(db, customer_id, endpoint_id, endpoint_update)


# Decativate webhook endpoint
def deactivate_webhook_endpoint(db : Session, customer_id : int, endpoint_id : int):
    return webhook_repository.deactivate_webhook_endpoint(db, customer_id, endpoint_id)


# Deliver webhook ( This corresponds to create_webhook_delivery() in repository.py)
# create_webhook_delivery() never gets its own pass-through in service.py because it's never called 
# directly from the router. It only ever gets called from inside deliver_webhook as the logging step.

# Also, one distinction from create_webhook_delivery() is that deliver_webhook() only takes
# as parameters in its signature the fields that are known at the time of creation, 
# that is , customer_id, event_type and payload
# the other fields are only known after the HTTP request is made.
def deliver_webhook(db : Session, customer_id : int, event_type : str, payload : dict):
    # Query for all active endpoints where the event is at the events list and matches the customer
    endpoints = db.execute(select(WebhookEndpoint).where
                (WebhookEndpoint.customer_id == customer_id,
                WebhookEndpoint.is_active == True,
                WebhookEndpoint.events.contains([event_type]))).scalars().all()
    


    # For each endpoint found, send an HTTP POST to their URL with a payload as the JSON body using httpx
    for endpoint in endpoints:
 
        try:
            # send the request
            response = httpx.post(endpoint.url, json=payload, timeout=10)
            
            # Check the response — did it succeed or fail?
            if response.status_code < 300:
                delivery_status = WebhookDeliveryStatus.DELIVERED
                response_status_code = response.status_code # retruns an interger (200, 404, 500,etc) similar to HTTP
                delivered_at = datetime.utcnow()
            else:
                delivery_status = WebhookDeliveryStatus.FAILED
                response_status_code = response.status_code
                delivered_at = None

        except httpx.RequestError as e:
            delivery_status = WebhookDeliveryStatus.FAILED
            response_status_code = None
            delivered_at = None
            logger.warning(f"Failed to deliver webhook to {endpoint.url}: {str(e)}")
            

        # Log the result by calling webhook_repository.create_webhook_delivery
        webhook_repository.create_webhook_delivery( db = db, webhook_endpoint_id = endpoint.id, event_type = event_type, payload = payload, status = delivery_status, response_status_code = response_status_code, retry_count = 0, delivered_at = delivered_at)







