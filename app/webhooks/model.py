from app.database import Base
from sqlalchemy.orm import relationship,  Mapped, mapped_column
from datetime import datetime
from typing import Optional , Any, Dict # to use with a dictionary with string keys and values of any type
from sqlalchemy.sql import func
from app.core.enums import WebhookDeliveryStatus
from sqlalchemy import DateTime, Enum as SQLAlchemyEnum, ForeignKey, JSON


class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    url: Mapped[str] = mapped_column()
    events: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    secret: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


    # Relationships
    webhook_deliveries = relationship("WebhookDelivery", back_populates="webhook_endpoint")
    customer = relationship("Customer", back_populates="webhook_endpoints")



class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    webhook_endpoint_id: Mapped[int] = mapped_column(ForeignKey("webhook_endpoints.id"))
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    status: Mapped[WebhookDeliveryStatus] = mapped_column(SQLAlchemyEnum(WebhookDeliveryStatus))
    response_status_code: Mapped[Optional[int]] = mapped_column()
    event_type: Mapped[str] = mapped_column()
    retry_count: Mapped[int] = mapped_column()
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


    # Relationships
    webhook_endpoint = relationship("WebhookEndpoint", back_populates="webhook_deliveries")