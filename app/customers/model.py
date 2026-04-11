from app.database import Base
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship,  Mapped, mapped_column
from datetime import datetime
from typing import Optional
from sqlalchemy.sql import func


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column() 
    stripe_customer_id: Mapped[str] = mapped_column(unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationship
    subscriptions = relationship("Subscription", back_populates="customer")
    invoices = relationship("Invoice", back_populates= "customer")
    webhook_endpoints = relationship("WebhookEndpoint", back_populates="customer")

