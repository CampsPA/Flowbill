from app.database import Base
from sqlalchemy.orm import relationship,  Mapped, mapped_column
from datetime import datetime
from sqlalchemy.sql import func
from typing import Optional 
from app.core.enums import InvoiceStatus
from sqlalchemy import  DateTime, Enum as SQLAlchemyEnum , ForeignKey


class Invoice(Base):
    
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id")) 
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[InvoiceStatus] = mapped_column(SQLAlchemyEnum(InvoiceStatus))
    amount_cents: Mapped[int] = mapped_column()
    currency: Mapped[str] = mapped_column()
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    line_items = relationship("LineItem", back_populates="invoice")
    payment_attempts = relationship("PaymentAttempt", back_populates="invoice")
    customer = relationship("Customer", back_populates="invoices")
    subscription = relationship("Subscription", back_populates="invoices")