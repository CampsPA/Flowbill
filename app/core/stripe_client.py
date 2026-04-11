# This file initialize the Stripe SDK with your secret key from config.py 
# and expose it to the rest of the application.

# Any module that needs to make an Strope API call will import from this file.

import stripe
from app.config import settings

stripe.api_key = settings.stripe_secret_key