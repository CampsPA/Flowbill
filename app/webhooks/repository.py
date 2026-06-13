# # Here we perform the actual CRUD operations against the database. 
# No business rules, no HTTP errors, just database in and database out.

# In this file we filter both by id and customer_id for security reasons, the rule for
# determining when to use this filter is if a table has a customer_id foreign_key.

from app.webhooks.schemas import WebhookEndpointCreate, WebhookEndpointUpdate
from app.webhooks.model import WebhookEndpoint, WebhookDelivery
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging
import secrets
from datetime import datetime
from app.core.enums import WebhookDeliveryStatus

logger = logging.getLogger("app.webhooks.repository")


# Create webhook endpoint
# include all fileds from the model which are not auto-generated, is_active is set to True on the model - no need to include it here
def create_webhook_endpoint(db : Session, webhook : WebhookEndpointCreate, customer_id : int):
    # Generate the secret
    secret = secrets.token_hex(32)
    new_webhook = WebhookEndpoint(url = webhook.url, events = webhook.events, customer_id = customer_id, secret=secret)
    db.add(new_webhook)
    db.commit()
    db.refresh(new_webhook)
    logger.info(f"Webhook with id {new_webhook.id} successfully created.")
    return new_webhook

# Create webhook endpoint by id
def get_webhook_endpoint_by_id(db : Session, endpoint_id : int, customer_id: int, ):
    endpoint = db.execute(select(WebhookEndpoint).where(WebhookEndpoint.id == endpoint_id, WebhookEndpoint.customer_id == customer_id)).scalar_one_or_none()

    if endpoint is None:
        logger.info(f"No endpoint found with id {endpoint_id}.")
        return None
    else:
        logger.info(f"Endpoint with endpoint_id {endpoint_id} successfully retrieved.")
    return endpoint

# Get webhook endpoint by endpoint_id only - used by deliver endpoint
# which needs to find the endpoint regardless of customer to get its customer_id
def get_webhook_endpoint_by_id_only(db: Session, endpoint_id: int):
    endpoint = db.execute(select(WebhookEndpoint).where(WebhookEndpoint.id == endpoint_id)).scalar_one_or_none()
    if endpoint is None:
        logger.info(f"No endpoint found with id {endpoint_id}.")
        return None
    return endpoint


# get webhook endpoint by url
def get_webhook_endpoint_by_url(db : Session, url : str, customer_id : int):
    endpoint = db.execute(select(WebhookEndpoint).where(WebhookEndpoint.url == url, WebhookEndpoint.customer_id == customer_id)).scalar_one_or_none()

    if endpoint is None:
        logger.info(f"No endpoint found with url {url}.")
        return None
    else:
        logger.info(f"Endpoint with url {url} successfully retrieved.")
    return endpoint


# Get all webhook endpoints ( by customer)
def get_all_webhook_endpoints(db : Session, customer_id : int):
    endpoints = db.execute(select(WebhookEndpoint).where(WebhookEndpoint.customer_id == customer_id)).scalars().all()
    return endpoints


# Update webhook endpoint
def update_webhook_endpoint(db : Session,customer_id : int, endpoint_id : int, endpoint_update : WebhookEndpointUpdate):
    endpoint = db.execute(select(WebhookEndpoint).where(WebhookEndpoint.id == endpoint_id, WebhookEndpoint.customer_id == customer_id)).scalar_one_or_none()

    if not endpoint:
        logger.info("Endpoint not found")
        return None

    #  Extract only set fields
    updated_data = endpoint_update.model_dump(exclude_unset=True)
    
    #  Apply changes
    for key, value in updated_data.items():
        setattr(endpoint, key, value)
    

    db.commit()
    db.refresh(endpoint)
    return endpoint

    
# Decativate webhook endpoint
def deactivate_webhook_endpoint(db : Session, customer_id : int, endpoint_id : int):
    endpoint = db.execute(select(WebhookEndpoint).where(WebhookEndpoint.id == endpoint_id, WebhookEndpoint.customer_id == customer_id)).scalar_one_or_none()

    if not endpoint:
        logger.info("Endpoint not found")
        return None
    
    # Cancel webhook endpoint
    endpoint.is_active = False
    logger.info(f"Endpoint with id {endpoint_id} successfully cancelled.")

    db.commit()
    db.refresh(endpoint)
    return endpoint


# Create webhook Delivery endpoint
def create_webhook_delivery(db: Session, webhook_endpoint_id: int, event_type: str, payload: dict, status: WebhookDeliveryStatus, response_status_code: int | None, retry_count: int, delivered_at: datetime | None):
    new_webhook = WebhookDelivery(webhook_endpoint_id = webhook_endpoint_id, event_type = event_type, payload = payload, status = status, response_status_code = response_status_code, retry_count = retry_count, delivered_at = delivered_at)
    db.add(new_webhook)
    db.commit()
    db.refresh(new_webhook)
    logger.info(f"Webhook with id {new_webhook.id} successfully created.")
    return new_webhook

