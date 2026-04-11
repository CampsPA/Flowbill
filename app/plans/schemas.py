# defines data shapes: PlanCreate, PlanUpdate, PlanResponse

from pydantic import BaseModel,ConfigDict
from datetime import datetime
from app.core.enums import PlanInterval
from typing import  Any, Dict # to use with a dictionary with string keys and values of any type

class PlanCreate(BaseModel):
    # Think of this in terms of what fields does an admin provide when creating a new plan?
    name : str
    price_cents : int
    interval : PlanInterval
    trial_days : int | None = None
    features : Dict[str, Any] |None = None


class PlanUpdate(BaseModel):
    # Think of it in terms of data that can be changed at some point in the future
    # Here all fields are optional because the admin can change them, not because they
    # were defined as optional in the db model
    name : str |None = None
    price_cents : int |None = None
    interval : PlanInterval |None = None
    trial_days : int | None = None
    features : Dict[str, Any] |None = None
    is_active : bool |None = None


class PlanResponse(BaseModel):
    # Think of it in terms of data that can be safely displayed
    id : int
    name : str
    price_cents : int
    interval : PlanInterval
    trial_days : int | None = None
    features : Dict[str, Any] |None = None
    is_active : bool
    created_at : datetime

    model_config =ConfigDict(from_attributes=True)