# Handles authentication business logic — user creation and retrieval.
# Security utilities (hashing, tokens) are delegated to app/core/security.py.


from sqlalchemy.orm import Session
from sqlalchemy import select
from app.auth.schemas import UserCreate
from app.auth.model import User
import logging

# Import security utilities
from app.core.security import hash_password

# Get a logger instance
logger = logging.getLogger("app.auth.service")



# Create user
def create_user(db : Session, user: UserCreate):
    hashed_password = hash_password(user.password)
    new_user = User(email= user.email,hashed_password = hashed_password, name=user.name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User with id {new_user.id} successfully created.")
    return new_user
    
# Get the user by email
def get_user_by_email(db : Session, email : str):
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none() # SQLAlchemy 2.0 query style

    if user is None:
        logger.info(f"No user found.")
        return None
    else:
        logger.info("User successfully retrieved.")
    return user



