from slowapi import Limiter
from slowapi.util import get_remote_address
from .config import settings
from fastapi import Request
from app.core.security import verify_access_token

# Defina a limite with an IP-based function for unauthenticated endpoints like auth
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"], storage_uri=f"redis://{settings.redis_host}:{settings.redis_port}" )

# Built the user ID-based key function for authenticated endpoints like analysis, portfolios, holdings
def get_current_user_key(request: Request):
    # extract token from header
    token = request.headers.get("Authorization")
    if not token:
        return get_remote_address(request)
    # Strip the Bearer prefix from the token
    token = token.replace("Bearer ", "")
    # decode the token
    try:
        token_data = verify_access_token(token, Exception()) # this comes from oauth2 and it contains the email
        return token_data.email # simply return the email sting contained inside token_data
    except Exception:
        # return email as the key
        return get_remote_address(request) # extracts the client's IP address and returns a string

    