# defines HTTP endpoints and delegates to the service layer

from fastapi import Depends, APIRouter
from app.invoices.schemas import InvoiceCreate, InvoiceResponse, InvoiceUpdate
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
import logging
from app.invoices import service
# from ..limiter import limiter - it will be created at phase 6
# PDF router
from fastapi.responses import Response


# Get a logger instance
logger = logging.getLogger("app.invoices.router")

# Instantiate a router
router = APIRouter(tags=['Invoices']) 


# Create invoice endpoint
@router.post('/', response_model=InvoiceResponse)
#@limiter.limit("5/minute")
def create_invoice(invoice_data: InvoiceCreate, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.create_invoice(db, invoice_data)


# I3: moved /subscription/{subscription_id} ABOVE /{invoice_id} so FastAPI does not
# greedily match the literal segment "subscription" as an invoice_id integer.
# Get invoices by subscription_id, response model as a list
@router.get('/subscription/{subscription_id}', response_model=list[InvoiceResponse])
#@limiter.limit("5/minute")
def get_invoice_by_subscription(subscription_id : int, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.get_invoices_by_subscription(db, subscription_id)


# PDF endpoint step #14 PDF document
@router.get('/{invoice_id}/pdf')
#@limiter.limit("5/minute")
def pdf_creation(invoice_id: int , customer_id: int , db: Session = Depends(get_db),current_user = Depends(get_current_user)):
    pdf_bytes = service.get_invoice_pdf(db, invoice_id, customer_id)
    return Response(content=pdf_bytes, media_type='application/pdf', headers={'Content-Disposition': f'attachment; filename=invoice_{invoice_id}.pdf'})


# Get invoice by id
@router.get('/{invoice_id}', response_model=InvoiceResponse)
#@limiter.limit("5/minute")
def get_invoice_by_id(invoice_id : int, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.get_invoice_by_id(db, invoice_id)


# Get all invoices (needs db and customer_id), response model as a list
@router.get('/', response_model=list[InvoiceResponse])
#@limiter.limit("5/minute")
def get_all_invoices(customer_id : int, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.get_all_invoices(db, customer_id)


# Update invoice (invoice_id)
@router.patch('/{invoice_id}', response_model=InvoiceResponse)
#@limiter.limit("5/minute")
def update_invoice(invoice_id : int, invoice_update : InvoiceUpdate, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.update_invoice(db, invoice_id, invoice_update)





# Note on Avoiding conflicting paths
# When two GET endpoints on the same router {invoice_id and subscription_id use a path parameter, 
# FastAPI can't distinguish between them.
# '/subscription/{subscription_id}'
