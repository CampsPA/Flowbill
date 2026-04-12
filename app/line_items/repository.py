# Here we perform the actual CRUD operations against the database. 
# No business rules, no HTTP errors, just database in and database out.

from app.line_items.schemas import LineItemCreate, LineItemUpdate
from app.line_items.model import LineItem
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging

logger = logging.getLogger("app.line_items.repository")


# Create line item
def create_line_item(db : Session, line_item : LineItemCreate):
    new_line_item = LineItem(invoice_id = line_item.invoice_id, description = line_item.description,
                             amount_cents = line_item.amount_cents, quantity = line_item.quantity)
    
    db.add(new_line_item)
    db.commit()
    db.refresh(new_line_item)
    logger.info(f"Line Item with id {new_line_item.id} successfully created.")
    return new_line_item
    

# Get line item by id
def get_line_item_by_id(db : Session, line_item_id : int):
    line_item = db.execute(select(LineItem).where(LineItem.id == line_item_id)).scalar_one_or_none()
    return line_item


# Get line items by invoice (filter by invoice_id)

def get_line_item_by_invoice(db : Session, invoice_id : int):
    line_item = db.execute(select(LineItem).where(LineItem.invoice_id == invoice_id)).scalars().all()
    return line_item


# Update line item
def update_line_item(db: Session, line_item_id : int, line_item_update : LineItemUpdate):
    line_item = db.execute(select(LineItem).where(LineItem.id == line_item_id)).scalar_one_or_none()

    if not line_item:
        logger.info("Line item not found")
        return None

    #  Extract only set fields
    line_item_update = line_item_update.model_dump(exclude_unset=True)
    
    #  Apply changes
    for key, value in line_item_update.items():
        setattr(line_item, key, value)
    

    db.commit()
    db.refresh(line_item)
    return line_item




