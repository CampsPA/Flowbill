# defines HTTP endpoints and delegates to the service layer

from fastapi import Depends, APIRouter, Request
from app.line_items.schemas import LineItemCreate, LineItemResponse, LineItemUpdate
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
import logging
from app.line_items import service
from app.limiter import limiter


# Get a logger instance
logger = logging.getLogger("app.line_items.router")

# Instantiate a router
router = APIRouter(tags=['LineItems'])

# Create line item
@limiter.limit("5/minute")
@router.post('/', response_model= LineItemResponse)
def create_line_item(request: Request, line_item_data : LineItemCreate, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.create_line_item(db, line_item_data)


# Get line item by id
@limiter.limit("5/minute")
@router.get('/{line_item_id}', response_model= LineItemResponse)
def get_line_item_by_id(request: Request, line_item_id : int, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.get_line_item_by_id(db, line_item_id)


# Get line items by invoice (filter by invoice_id, return as sa list)
@limiter.limit("5/minute")
@router.get('/invoice/{invoice_id}', response_model= list[LineItemResponse])
def get_line_items_by_invoice(request: Request, invoice_id : int, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.get_line_item_by_invoice(db, invoice_id)


# Update line item
@limiter.limit("5/minute")
@router.patch('/{line_item_id}', response_model= LineItemResponse)
def update_line_item(request: Request, line_item_id : int, line_item_update : LineItemUpdate, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.update_line_item(db, line_item_id, line_item_update)
