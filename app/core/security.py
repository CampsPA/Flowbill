# Handles security utilities

import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timezone, timedelta
from app.auth.schemas import TokenData
from pwdlib import PasswordHash
import logging
from app.config import settings


# Get a logger instance
logger = logging.getLogger("app.core.security")


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