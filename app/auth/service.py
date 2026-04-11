
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timezone, timedelta
from app.auth.schemas import TokenData
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.auth.schemas import UserCreate
from app.auth.model import User
from app.config import settings
import logging
from pwdlib import PasswordHash


# Get a logger instance
logger = logging.getLogger("app.auth.service")




SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# Hash password
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

# Create a function to compared the hashed login password to the hashed_password in the database
# Takes the attempeted login password, hash it then compared to the one stored in the database
def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)


# Create a function to generate tokens
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # reference from .env
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Log sucessful token creation
    logger.info("Token successfully generated.")

    return encoded_jwt



# Create a function to verify/decode the tokens
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
        logger.info("Token decoded and validated.") # Happy path log
    except InvalidTokenError:
        logger.warning("Token could not be  validated.") # Invalid or expired token
        raise credentials_exception

    
    return token_data


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



