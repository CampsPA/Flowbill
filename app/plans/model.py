from app.database import Base
from sqlalchemy.orm import relationship,  Mapped, mapped_column
from datetime import datetime
from sqlalchemy.sql import func
from typing import Optional , Any, Dict # to use with a dictionary with string keys and values of any type
from app.core.enums import PlanInterval # import the PlanInterval from enums.py
from sqlalchemy import  DateTime, Enum as SQLAlchemyEnum, JSON # we alias Enum as SQLAlchemyEnum beacuse we already import enum 
# in enums.py and we don't want ti to clash if the use enum here as well 

class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True) 
    price_cents: Mapped[int] = mapped_column() 
    interval: Mapped[PlanInterval] = mapped_column(SQLAlchemyEnum(PlanInterval))
    trial_days: Mapped[Optional[int]] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    features: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON) 
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

    # Relationship
    subscriptions = relationship("Subscription", back_populates="plan")
    
