from app.database import Base
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column() 
    hashed_password: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    
    # No relationships 
    # The users table represents the operators of the FlowBill system — 
    # the admins who log in and manage billing. 
    # They have no relationship to customers, subscriptions, invoices, 
    # or any of the billing domain tables.
    
