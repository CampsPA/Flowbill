# run app : uvicorn app.main:app --reload

from fastapi import FastAPI, Request # Request is used for the custom exception handlers
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.auth.router import router as auth_router # alias the router specifically for the file
from app.customers.router import router as customers_router
from app.plans.router import router as plans_router
from app.subscriptions.router import router as subscriptions_router
from app.invoices.router import router as invoices_router
from app.line_items.router import router as line_items_router
from app.webhooks.router import router as webhook_router
from app.webhooks.stripe_receiver import router as stripe_receiver_router
from app.payments.router import router as payments_router
from app.tenant_settings.router import router as tenant_settings_router
# Import logging
from app.core.logging import setup_logging 
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
from app.tenant_settings.model import TenantSettings
# APScheduler
from contextlib import asynccontextmanager # to use the lifespan function
from apscheduler.schedulers.asyncio import  AsyncIOScheduler # since fast api runs on asyncio and I needed the scheduler to share the same event loop
# Cycle runner
from app.billing.cycle_runner import run_billing_cycle
# Duning
from app.billing.dunning import run_dunning
# Custom exceptions
from app.core.exceptions import ResourceNotFound, DuplicateRecord, ExternalServiceError, PermissionDeniedError
from starlette.responses import JSONResponse
# FastApi Integration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

# Call the logging setup function *before* initializing the FastAPI app or getting other loggers
setup_logging()


# Initialize Sentry
# Add FastApiIntegration to automatically capture request context like URL, HTTP Method,
# and request body when an exception occurs.
sentry_sdk.init(dsn= settings.sentry_dsn,
    send_default_pii=True, integrations=[StarletteIntegration() ,FastApiIntegration()]
)


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
    # Add a run_billing_cyc;e_job
    scheduler.add_job(run_billing_cycle, 'interval', hours=24) # comes from cycle_runner billing cycle function.
    # add duuning job
    scheduler.add_job(run_dunning, 'interval', hours=24)
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


# Register custom exception handlers so that they are available when the routes are called
@app.exception_handler(ResourceNotFound)
async def resource_not_found_handler(request : Request, exc: ResourceNotFound):
    return JSONResponse(status_code= 404, content= {"detail" : exc.message})


@app.exception_handler(DuplicateRecord)
async def duplicated_record_handler(request : Request, exc: DuplicateRecord):
    return JSONResponse(status_code= 400, content= {"detail" : exc.message})


@app.exception_handler(ExternalServiceError)
async def external_service_handler(request : Request, exc: ExternalServiceError):
    return JSONResponse(status_code= 502, content= {"detail" : exc.message})



@app.exception_handler(PermissionDeniedError)
async def permission_denied_handler(request : Request, exc: PermissionDeniedError):
    return JSONResponse(status_code= 403, content= {"detail" : exc.message})




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

app.include_router(line_items_router, prefix="/line-items")
logger.info("Line items router successfully registered")

app.include_router(webhook_router, prefix="/webhooks")
logger.info("Webhooks router successfully registered")

app.include_router(stripe_receiver_router, prefix="/stripe/webhook")
logger.info("Stripe webhook router successfully registered")

app.include_router(payments_router, prefix="/payments")
logger.info("Payments router successfully registered")

app.include_router(tenant_settings_router, prefix="/tenant-settings")
logger.info("Tenant settings router successfully registered")





