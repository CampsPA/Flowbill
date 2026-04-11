from app.database import Base
from sqlalchemy.orm import relationship,  Mapped, mapped_column
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import DateTime, ForeignKey


class LineItem(Base):
    __tablename__ = "line_items"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    description: Mapped[str] = mapped_column()
    
    amount_cents: Mapped[int] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    invoice = relationship('Invoice', back_populates = "line_items")