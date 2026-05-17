from app.database import Base
from sqlalchemy.orm import  Mapped, mapped_column
from sqlalchemy import ForeignKey
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import  DateTime 

class TenantSettings(Base):
    __tablename__ = 'tenant_settings'

    id : Mapped[int] = mapped_column(primary_key=True) # no 'unique' since primary key already implies uniqueness
    customer_id : Mapped[int] = mapped_column(ForeignKey("customers.id"), unique=True)
    company_name : Mapped[str] = mapped_column()
    logo_url : Mapped[str] = mapped_column(nullable=True)
    address : Mapped[str] = mapped_column(nullable=True)
    brand_color : Mapped[str] = mapped_column(nullable=True)
    email_footer : Mapped[str] = mapped_column(nullable=True)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())

    # No relationship needed - the PDF generation function fetches settings by customer_id
    # directly,  it never navigates from a Customer object to its TenantSettings.