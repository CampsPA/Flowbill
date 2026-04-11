# Here we perform the actual CRUD operations against the database. 
# No business rules, no HTTP errors, just database in and database out.

from app.plans.schemas import PlanCreate, PlanUpdate
from app.plans.model import Plan
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging

logger = logging.getLogger("app.plans.repository")


# Create plan
def create_plan(db : Session, plan: PlanCreate):
    new_plan = Plan(name = plan.name, price_cents = plan.price_cents, interval = plan.interval,
                    trial_days = plan.trial_days, features = plan.features)
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    logger.info(f"Plan with id {new_plan.id} successfully created.")
    return new_plan


# Get plan by id
def get_plan_by_id(db : Session, plan_id : int): # here I create plan_id as a write the function
    plan = db.execute(select(Plan).where(Plan.id == plan_id)).scalar_one_or_none() # SQLAlchemy 2.0 query style
    
    if plan is None:
        logger.info(f"No plan found with id {plan_id}.")
        return None
    else:
        logger.info(f"Plan with plan_id {plan_id} successfully retrieved.")
    return plan



# Get all plans
def get_all_plans(db: Session):
    plans = db.execute(select(Plan)).scalars().all()
    logger.info(f"Retrieved all plans.")
    return plans


# Get plan by name
def get_plan_by_name(db : Session, name : str):
    plan = db.execute(select(Plan).where(Plan.name == name)).scalar_one_or_none() # SQLAlchemy 2.0 query style
    
    if plan is None:
        logger.info(f"No plan found with name: {name}.")
        return None
    else:
        logger.info(f"Plan with name {name} successfully retrieved.")
    return plan


# Update plan
def update_plan(db: Session, plan_id : int, plan_update : PlanUpdate):
    plan = db.execute(select(Plan).where(Plan.id == plan_id)).scalar_one_or_none() # SQLAlchemy 2.0 query style
    if not plan:
        logger.info("Plan not found")
        return None

    #  Extract only set fields
    plan_update = plan_update.model_dump(exclude_unset=True)
    
    #  Apply changes
    for key, value in plan_update.items():
        setattr(plan, key, value)
    

    db.commit()
    db.refresh(plan)
    return plan


# Deactivate plan (delete)
def deactivate_plan(db: Session, plan_id : int):
    plan = db.execute(select(Plan).where(Plan.id == plan_id)).scalar_one_or_none() # SQLAlchemy 2.0 query style

    if not plan:
        logger.info("Plan not found")
        return None
    
    # Deactivate plan - set is_active to false
    plan.is_active = False

    db.commit()
    db.refresh(plan)
    return plan

