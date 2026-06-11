# defines data shapes: WebhookEndpointCreate, WebhookEndpointUpdate, WebhookEndpointResponse

#In this module a webhook endpoint is a notification preference — 
# the customer is saying:
# "When these specific events happen in my account, tell me about it at this URL."


from pydantic import BaseModel,ConfigDict
from datetime import datetime


# Data coming in to the API (provided by user)
class WebhookEndpointCreate(BaseModel):
    # Think of this in terms of what would you ask from the client inorder to register the URL
    url : str # where should the notification be sent
    events : list[str] # which events are important to the client


# Data going out from the API
class WebhookEndpointUpdate(BaseModel):
    # Think of it in terms of data that can be changed at some point in the future
    # All fields optional (for editing)
    customer_id: int  # which customer is registering this endpoint
    url : str | None = None # client may change where where he wants the url to be sent
    events : list[str] | None = None # client may wnat to add or remove an event
    



# Data going out from the API
class WebhookEndpointResponse(BaseModel):
    # Think of it in terms of data that can be safely displayed
    id : int
    customer_id : int
    url : str
    events : list[str]
    is_active : bool
    created_at : datetime

    model_config = ConfigDict(from_attributes=True) # only add when data is returned, not reveived



# Here we create WebhookEndpointCreateResponse to be used by the POST when creating the registration
# This is the only time the secret is returned so the client can save it and use it to verify
# that the notifications actually come from FlowBill
class WebhookEndpointCreateResponse(WebhookEndpointResponse):
    # Note how this class inherits everything from WebhookEndpointResponse, then adds the secret
    secret : str

    model_config = ConfigDict(from_attributes=True) # only add when data is returned, not reveived


# Create the schema so that deliver_webhook_endpoint() can use event_type and payload
class WebhookDeliverRequest(BaseModel):
    event_type : str
    payload : dict