from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context
from app.config import settings
from app.database import Base
# Add models for migrations
from app.customers.model import Customer
from app.plans.model import Plan
from app.subscriptions.model import Subscription
from app.invoices.model import Invoice
from app.line_items.model import LineItem
from app.payments.model import PaymentAttempt
from app.webhooks.model import WebhookEndpoint, WebhookDelivery
from app.auth.model import User
from app.tenant_settings.model import TenantSettings


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = (
        f"postgresql://{settings.database_username}:{settings.database_password}"
        f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
    )
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = (
        f"postgresql://{settings.database_username}:{settings.database_password}"
        f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
    )
    connectable = create_engine(url)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()