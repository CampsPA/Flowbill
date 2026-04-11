from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


# Data coming in to the API (provided by user)
class CustomerCreate(BaseModel): 
    # Think of this in terms of what would you ask from the customer to create an account
    email : EmailStr
    name : str


# Data going out from the API
class CustomerUpdate(BaseModel):
    # Think of it in terms of data that can be changed at some point in the future
    email: EmailStr | None = None # can change email
    name:  str  | None = None # can change name
    is_active: bool | None = None # can change status -> yes/no
 

# Data going out from the API
class CustomerResponse(BaseModel): 
    # Think of it in terms of data that can be safely displayed
    id : int
    email : EmailStr
    name : str
    is_active : bool
    stripe_customer_id : str | None = None
    created_at : datetime 
    

    model_config =ConfigDict(from_attributes=True) # only add when data is returned, not reveived
