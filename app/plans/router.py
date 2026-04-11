# defines HTTP endpoints and delegates to the service layer

from fastapi import Depends, APIRouter
from app.plans.schemas import PlanCreate, PlanResponse, PlanUpdate
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
import logging
from app.plans import service
# from ..limiter import limiter - it will be created at phase 6


# Get a logger instance
logger = logging.getLogger("app.plans.router")

# Instantiate a router
router = APIRouter(tags=['Plans']) 


# Create plan endpoint
@router.post('/',response_model=PlanResponse)
#@limiter.limit("5/minute")
def create_plan(plan_data: PlanCreate, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.create_plan(db, plan_data)


# Get plan by id endpoint
@router.get('/{plan_id}', response_model=PlanResponse)
#@limiter.limit("5/minute")
def get_plan_by_id(plan_id : int, db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.get_plan_by_id(db, plan_id)


# Get all plans
@router.get('/', response_model=list[PlanResponse])
#@limiter.limit("5/minute")
def get_plans(db:Session = Depends(get_db), current_user= Depends(get_current_user)):
    return service.get_all_plans(db)


# Update plan
@router.patch('/{plan_id}', response_model=PlanResponse)
#@limiter.limit("5/minute")
def update_plan(plan_id : int, plan_update : PlanUpdate, db:Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.update_plan(db, plan_id, plan_update)


# Deactivate (delete) plans
@router.delete('/{plan_id}', response_model=PlanResponse)
#@limiter.limit("5/minute")
def deactivate_plan(plan_id : int, db : Session = Depends(get_db), current_user = Depends(get_current_user)):
    return service.deactivate_plan(db, plan_id)
