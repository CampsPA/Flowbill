# Defines data shape, TenantSettingsCreate, TenantSettingsUpdate, TenantSettingsResponse


from pydantic import BaseModel,ConfigDict
from datetime import datetime


class TenantSettingsCreate(BaseModel):
    company_name : str
    logo_url : str |None = None
    address : str |None = None
    brand_color : str |None = None
    email_footer : str |None = None



class TenantSettingsUpdate(BaseModel):
    company_name : str |None = None
    logo_url : str |None = None
    address : str |None = None
    brand_color : str |None = None
    email_footer : str |None = None


class TenantSettingsResponse(BaseModel):
    id : int 
    customer_id : int
    company_name : str 
    logo_url : str |None = None
    address : str |None = None
    brand_color : str |None = None
    email_footer : str |None = None
    created_at : datetime


    model_config =ConfigDict(from_attributes=True)

