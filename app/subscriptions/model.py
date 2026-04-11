from app.database import Base
from sqlalchemy.orm import relationship,  Mapped, mapped_column
from datetime import datetime
from sqlalchemy.sql import func
from typing import Optional 
from app.core.enums import SubscriptionStatus
from sqlalchemy import  DateTime, Enum as SQLAlchemyEnum , ForeignKey


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id")) 
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id")) 
    status: Mapped[SubscriptionStatus] = mapped_column(SQLAlchemyEnum(SubscriptionStatus))
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True)) 
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    cancel_at_period_end: Mapped[bool] = mapped_column(default=False) # Default is false because we don't wnat the subscrition to cancel at the end, we wnat to renew it.
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True)) # This is optional because thius date is not defined when the table is created
    paused_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True)) # This is optional because thius date is not defined when the table is created
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now()) # Uses server_default=func.now() beacuse it sets the date that the event was created
    
    # Relationship
    invoices = relationship("Invoice", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")
    customer = relationship("Customer", back_populates="subscriptions")
    
    #Note: 
    #Use server_default=func.now() for created_at because it is the date that the subscription 
    #is created. 
    #For future events such as current_period_start and current_period_end use DateTime(timezone=True,
    #For dates not defined at the time of the table's creation, use Optional - this will be populated
    #when the event takes place.
    
