# Defines data shape, SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse


from pydantic import BaseModel,ConfigDict
from datetime import datetime
from app.core.enums import SubscriptionStatus


class SubscriptionCreate(BaseModel):
    customer_id : int
    plan_id : int


class SubscriptionUpdate(BaseModel):
    plan_id : int | None = None
    status : SubscriptionStatus | None = None
    current_period_start : datetime | None = None
    current_period_end : datetime | None = None
    cancel_at_period_end : bool | None = None
    cancelled_at: datetime | None = None
    paused_at: datetime | None = None



class SubscriptionResponse(BaseModel):
    id : int 
    customer_id : int
    plan_id : int
    status : SubscriptionStatus
    current_period_start : datetime 
    current_period_end : datetime 
    cancel_at_period_end : bool 
    cancelled_at: datetime | None = None
    paused_at: datetime | None = None
    created_at : datetime

    model_config =ConfigDict(from_attributes=True)