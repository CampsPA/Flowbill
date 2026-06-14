# defines HTTP endpoints and delegates to the service layer

from fastapi import Depends, APIRouter, Request
from app.tenant_settings.schemas import TenantSettingsUpdate, TenantSettingsResponse
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
import logging
from app.tenant_settings import service
from app.limiter import limiter


# Get a logger instance
logger = logging.getLogger("app.tenant_settings.router")

# Instantiate a router
router = APIRouter(tags=['Tenants Settings'])


# Create an endpoint to create/update tenant settings - upserting for logged-in customer
@router.put('/{customer_id}', response_model= TenantSettingsResponse)
@limiter.limit("5/minute")
def upsert(request: Request, customer_id: int, tenant_settings_update : TenantSettingsUpdate, db:Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.upsert_settings(db, customer_id, tenant_settings_update)

# Create an endpoint to retrieve settings for logged-in customers
@router.get('/{customer_id}', response_model= TenantSettingsResponse)
@limiter.limit("5/minute")
def get_settings(request: Request, customer_id: int, db:Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.get_settings(db, customer_id)
