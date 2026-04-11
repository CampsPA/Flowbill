from enum import Enum

class PlanInterval(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"

class SubscriptionStatus(str, Enum):
    ACTIVE= "active"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    PAST_DUE = "past_due"

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"

class PaymentAttemptStatus(str, Enum):
    SUCCEEDED =  "succeeded"
    FAILED = "failed"

class WebhookDeliveryStatus(str, Enum):
    PENDING =  "pending"
    DELIVERED = "delivered"
    FAILED = "failed"