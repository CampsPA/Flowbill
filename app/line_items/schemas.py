# defines data shapes: LineItemCreate, LineItemUpdate, LineItemResponse

from pydantic import BaseModel,ConfigDict
from datetime import datetime


class LineItemCreate(BaseModel):
    # Think of this in terms of what fields does an admin provide when entering a lineItem
    invoice_id : int
    description : str
    amount_cents : int
    quantity : int

class LineItemUpdate(BaseModel):
    # Think of it in terms of data that can be changed at some point in the future
    # Here all fields are optional because the admin can change them, not because they
    # were defined as optional in the db model
    invoice_id : int | None = None
    description : str | None = None
    amount_cents : int | None = None
    quantity : int | None = None


class LineItemResponse(BaseModel):
    # Think of it in terms of data that can be safely displayed
    id : int
    invoice_id : int
    description : str
    amount_cents : int
    quantity : int
    created_at : datetime

    model_config = ConfigDict(from_attributes=True)

