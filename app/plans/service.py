# enforces business rules and raises errors before delegating to the repository

from app.plans import repository # this imports all functions from repository.py
from app.plans.schemas import PlanCreate, PlanUpdate
from sqlalchemy.orm import Session
import logging
# Custom exceptions
from app.core.exceptions import DuplicateRecord, ResourceNotFound
# Plans DELETE: import subscriptions model to check for active subscribers
from sqlalchemy import select
from app.subscriptions.model import Subscription
from app.core.enums import SubscriptionStatus
from fastapi import HTTPException  # Plans DELETE: needed to return 400 if active subs exist


logger = logging.getLogger("app.plans.service")

# Create plan
def create_plan(db : Session, plan: PlanCreate):
    # Check plan name, if user exists raise error, if not create user
    existing_plan = repository.get_plan_by_name(db, plan.name)
    if  existing_plan is not None:
        logger.info(f"Plan with name {plan.name} already registered.")
        raise DuplicateRecord("name", plan.name)
        
    
    return repository.create_plan(db, plan)


# Get plan by id
def get_plan_by_id(db : Session, plan_id : int):
    return repository.get_plan_by_id(db, plan_id)


# Get all plans
def get_all_plans(db: Session):
    return repository.get_all_plans(db)


# Get plan by name
def get_plan_by_name(db : Session, name : str):
    return repository.get_plan_by_name(db, name)



# Update plan
def update_plan(db: Session, plan_id : int, plan_update : PlanUpdate):
    plan = repository.get_plan_by_id(db, plan_id)

    if plan is None:
        raise ResourceNotFound("Plan", plan_id)
    return repository.update_plan(db, plan_id, plan_update)


# Deactivate plan (delete)
def deactivate_plan(db: Session, plan_id : int):
    plan = repository.get_plan_by_id(db, plan_id)

    if plan is None:
        raise ResourceNotFound("Plan", plan_id)

    # Plans DELETE: block deactivation if any active subscribers exist on this plan
    active_sub_count = db.execute(
        select(Subscription).where(
            Subscription.plan_id == plan_id,           # only for this plan
            Subscription.status == SubscriptionStatus.ACTIVE  # only active ones
        )
    ).scalars().all()
    if active_sub_count:
        # Plans DELETE: return 400 rather than silently deactivating with live subscribers
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a plan with active subscribers. Deactivate it instead."
        )

    return repository.deactivate_plan(db, plan_id)