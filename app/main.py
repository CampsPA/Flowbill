# run app : uvicorn app.main:app --reload

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.auth.router import router as auth_router # alias the router specifically for the file
from app.customers.router import router as customers_router
from app.plans.router import router as plans_router
from app.subscriptions.router import router as subscriptions_router
from app.invoices.router import router as invoices_router
from app.line_items.router import router as line_items_router
#from app.logger import setup_logging
# SlowAPI
#from app.limiter import limiter
#from slowapi import _rate_limit_exceeded_handler
#from slowapi.errors import RateLimitExceeded
# Sentry
import sentry_sdk
from app.config import settings
# Import all models for relationships
from app.customers.model import Customer
from app.plans.model import Plan
from app.subscriptions.model import Subscription
from app.invoices.model import Invoice
from app.line_items.model import LineItem
from app.payments.model import PaymentAttempt
from app.webhooks.model import WebhookEndpoint, WebhookDelivery
from app.auth.model import User
# APScheduler
from contextlib import asynccontextmanager # to use the lifespan function
from apscheduler.schedulers.asyncio import  AsyncIOScheduler # since fast api runs on asyncio and I needed the scheduler to share the same event loop


# Initialize Sentry
sentry_sdk.init(dsn= settings.sentry_dsn,
    send_default_pii=True,
)


# Call the logging setup function *before* initializing the FastAPI app or getting other loggers
#setup_logging()

# Get logger instance 
# app.main is a child of app so it inherits everything automatically
logger = logging.getLogger("app.main")

# Instantiate the scheduler
scheduler = AsyncIOScheduler()

# APScheduler lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    # start the scheduler, add the billing cycle job
    scheduler.start()
    # App startup complete
    logger.info("Flowbill starting up.")
    # Add a job
    #scheduler.add_job(run_billing_cycle, 'interval', hours=24)
    yield
    # shut down the scheduler
    scheduler.shutdown()
    logger.info("Flowbill shutting down.")


# Initialize the App
app = FastAPI(
    title="Flowbill Subscription Billing Engine",
    description="Manages subscription billing for business and individuals",
    version="0.1.0",
    lifespan=lifespan
)

# Attach the limiter to the app state
#app.state.limiter = limiter

# Register (add) the exception handler
#app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Initialize CORS, provide the path to React - where frontend runs: http://localhost:3000
# CORS origins — localhost:3000 (future React app), localhost:5173 (placeholder UI dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message" : "Flowbill Subscription Billing Engine"}



# link routes -> add them as they are created
app.include_router(auth_router, prefix="/auth")
logger.info("Authentication router successfully registered.")

app.include_router(customers_router, prefix="/customers")
logger.info("Customers router successfully registered.")

app.include_router(plans_router, prefix="/plans")
logger.info("Plans router successfully registered")

app.include_router(subscriptions_router, prefix="/subscriptions")
logger.info("Subscriptions router successfully registered")

app.include_router(invoices_router, prefix="/invoices")
logger.info("Invoices router successfully registered")

app.include_router(line_items_router, prefix="/line_items")
logger.info("Line items router successfully registered")




# Starup/ shutdown events for APIscheduler
