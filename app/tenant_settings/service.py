# Here we enforce business rules and raises errors before delegating database 
# operations to the repository.

from app.tenant_settings import repository # this imports all functions from repository.py
from sqlalchemy.orm import Session
import logging
from app.core.exceptions import ResourceNotFound
from app.tenant_settings.schemas import TenantSettingsUpdate


logger = logging.getLogger("app.tenant_settings.service")


# Create a function to check for existing record, creates and updates, returns a record
def upsert_settings(db : Session, customer_id : int, tenant_settings_update: TenantSettingsUpdate):
    return repository.upsert(db, customer_id, tenant_settings_update)

# Create a function to check whether the customer has ever created their tenant settings
def get_settings(db: Session, customer_id : int):
    # check 
    result = repository.get_by_customer_id(db, customer_id)

    if result is None:
        raise ResourceNotFound("TenantSettings", customer_id)
    
    return result
