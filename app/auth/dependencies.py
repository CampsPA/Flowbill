
from fastapi import status, HTTPException, Depends
from app.auth.model import User
from app.database import get_db
from sqlalchemy.orm import Session
import logging
from fastapi.security import OAuth2PasswordBearer
from app.auth.service import verify_access_token
from sqlalchemy import select

# Get a logger instance
logger = logging.getLogger("app.auth.dependencies")

# oauth2_scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Create a get_current_user function
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)
    user = db.execute(select(User).where(User.email == token_data.email)).scalar_one_or_none() # SQLAlchemy 2.0 query style
    logger.info("User successfully validated.")

    if user is None:
        logger.warning("Authenticated token references a user that does not exist in the database.")
        raise credentials_exception
    return user
