from fastapi import Depends, status, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.schemas import UserCreate, UserResponse, Token
from sqlalchemy.orm import Session
from app.auth.service import verify_password , create_access_token, create_user, get_user_by_email
from app.database import get_db
import logging
# from ..limiter import limiter - it will be created at phase 6


# Get a logger instance
logger = logging.getLogger("app.auth.router")

# Instantiate a router
router = APIRouter(tags=['Authentication']) # Describe the routers purpose 

# Create register endpoint
@router.post('/register',response_model=UserResponse)
#@limiter.limit("5/minute")
def register(user_credentials: UserCreate, db:Session = Depends(get_db)):
    # Check user email, if user exists raise error, if not create user
    existing_user = get_user_by_email(db, user_credentials.email)
    if  existing_user is not None:
        logger.info("User with email address already registered.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email already registered")
    
    # Create new user
    new_user = create_user(db, user_credentials)
    logger.info("User successfully registered.")
    return new_user


# Create login endpoint
@router.post('/login', response_model=Token)
#@limiter.limit("5/minute")
def login(form_data:OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    existing_user = get_user_by_email(db, form_data.username)
    if not existing_user:
        logger.warning("Invalid Credentials") # provide a generic information so an attacker has minimum details
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Credentials")
    
    # Calls the function to verify password
    if not verify_password(form_data.password, existing_user.hashed_password):
        logger.warning("Invalid Credentials") # provide a generic information so an attacker has minimum details
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Credentials")

    # Return token - note that the token is created in oauth2 then returned here
    access_token = create_access_token(data={"sub": existing_user.email})
    logger.info("Token successfully created.")
    return {"access_token": access_token, "token_type": "bearer"}

# provide a generic information so an attacker has minimum details (does not know exactly what he cant access)





