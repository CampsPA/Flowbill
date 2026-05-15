# defines data shapes: InvoiceCreate, InvoiceUpdate, InvoiceResponse

from pydantic import BaseModel,ConfigDict
from typing import Optional
from datetime import datetime
from app.core.enums import PaymentAttemptStatus

class PaymentAttemptResponse(BaseModel):
    id : int
    invoice_id : int
    attempted_at : datetime
    status : PaymentAttemptStatus
    failure_reason : Optional[str] = None # -> optional fields defauts to None: look up model.py
    stripe_payment_intent_id : str
    created_at : datetime


    model_config = ConfigDict(from_attributes=True)
