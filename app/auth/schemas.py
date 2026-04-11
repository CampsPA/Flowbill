from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

# Here we don't include a UserUpdate schema because in this application ,
# the users table represents an internal administrator - not a regular user who manages
# theur own account.

class UserCreate(BaseModel): # Data coming in to the API (provided by user)
    email : EmailStr
    name : str
    password : str # This is hashed_apssword in the model but simply password here


class UserResponse(BaseModel): # Data going out from the API
    id : int
    email : EmailStr
    name : str
    is_active : bool
    created_at : datetime 
    

    model_config =ConfigDict(from_attributes=True) # only add when data is returned, not reveived

# Create a TokenData schema
class TokenData(BaseModel):
    email: str| None = None

class Token(BaseModel):
    access_token: str
    token_type: str
