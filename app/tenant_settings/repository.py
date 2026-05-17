# Here we perform the actual CRUD operations against the database. 
# No business rules, no HTTP errors, just database in and database out.


from app.tenant_settings.model import TenantSettings
from app.tenant_settings.schemas import TenantSettingsUpdate
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging

logger = logging.getLogger("app.tenant_settings.repository")


# Create a function to get customer by ID - one record
def get_by_customer_id(db : Session, customer_id : int):
    tenant_settings = db.execute(select(TenantSettings).where(TenantSettings.customer_id == customer_id)).scalar_one_or_none()

    if tenant_settings is None:
        logger.info(f"No tenant settings found with id {customer_id}.")
        return None
    else:
        logger.info(f"Tenant settings with customer id {customer_id} successfully retrieved.")
    return tenant_settings
    
    

# Create a function to check for existing record, creates and updates, returns a record
def upsert(db : Session, customer_id : int,  tenant_settings_update: TenantSettingsUpdate):
    data = tenant_settings_update.model_dump(exclude_unset=True)
    existing_record = get_by_customer_id(db, customer_id)

    if existing_record is None:
        logger.info(f"No existing record found with id {customer_id}")
        # Create a new TenantSettings record using customer_id and data
        # Add it to the session, commit, refresh and retun it
        new_tenant_settings = TenantSettings(customer_id=customer_id, **data) # customer_id=customer_id assigns the value to the column -> (column==value)
        db.add(new_tenant_settings)
        db.commit()
        db.refresh(new_tenant_settings)
        return new_tenant_settings
    else:
        logger.info(f"Existing record  with id {customer_id} successfully retrieved")
        # Loop over data dict and update each field on the sxisting record
        # commit, refresh, return it
        for key, value in data.items():
            setattr(existing_record, key, value)
        db.commit()
        db.refresh(existing_record)
        return existing_record


    # Note

    # the loop here iterates over the data and sets key as the attribute name
    # value as the value assigned to the name
    # Ex: if data contains 
    # company_name = name as key
    # brand_color = color as the value, each iteraction adds:
    # name to the existing_record company_name
    # color to the existing_record brand_color
        

