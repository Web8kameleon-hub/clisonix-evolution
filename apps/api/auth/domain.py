from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class SubscriptionPlan(str, Enum):
    FREE = "free"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class UserRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    email: str
    full_name: str | None = None
    is_active: bool = True
    is_verified: bool = True
    subscription_plan: SubscriptionPlan = SubscriptionPlan.FREE
    stripe_customer_id: str | None = None

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "UserRecord":
        return cls.model_validate(document)
