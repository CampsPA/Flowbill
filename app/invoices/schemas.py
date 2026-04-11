# defines data shapes: InvoiceCreate, InvoiceUpdate, InvoiceResponse

from pydantic import BaseModel,ConfigDict, Field
from datetime import datetime
from app.core.enums import InvoiceStatus



class InvoiceCreate(BaseModel):
    subscription_id : int
    customer_id : int
    amount_cents : int
    currency : str = Field(default= "usd") # This is optional with a default value, not an absent or null value
    due_date : datetime


class InvoiceUpdate(BaseModel):
    status : InvoiceStatus | None = None
    amount_cents : int | None = None
    due_date : datetime | None = None
    paid_at : datetime | None = None


class InvoiceResponse(BaseModel):
    id : int
    subscription_id : int
    customer_id : int
    status : InvoiceStatus
    amount_cents : int
    currency : str # here we don't use the defaul value because we return the vallu that is in the database
    due_date : datetime
    paid_at : datetime | None = None # optional since this value is None until paynent is made
    created_at : datetime

    model_config = ConfigDict(from_attributes=True)


# In InvoiceCreate I use the default value for the currency as a fallback, if it is 
# not provided it defaults to "USD", then at InvoiceResponse I dont need to specify 
# the default since this is just returning tahe value for currency that is alredy
# recorded in the database 