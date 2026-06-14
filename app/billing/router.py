# Exposes a single POST /billing/run endpoint for demo/admin use.
# run_billing_cycle() manages its own DB session internally, so no db dependency is needed here.

from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.billing.cycle_runner import run_billing_cycle
import logging
from app.limiter import limiter 

logger = logging.getLogger("app.billing.router")

router = APIRouter(tags=['Billing'])


@router.post('/run', status_code=200)
@limiter.limit("5/minute")
def trigger_billing_cycle(current_user=Depends(get_current_user)):
    """
    Manually trigger one billing cycle run.
    Finds all active subscriptions whose current_period_end <= now(),
    creates invoices, and attempts payment via Stripe.
    FastAPI runs sync handlers in a thread pool, so this won't block the event loop.
    """
    logger.info(f"Manual billing cycle triggered by user {current_user.id}")
    run_billing_cycle()
    return {"message": "Billing cycle complete."}
