from __future__ import annotations

from dataclasses import dataclass

from src.billing import BillingPlan, get_plan, list_plans


@dataclass
class MockSubscription:
    user_id: str
    plan: BillingPlan
    status: str = "mock_active"

    def as_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "plan": self.plan.as_dict(),
            "status": self.status,
            "live_payment": False,
        }


class StripeBillingService:
    payment_provider = "stripe"

    def __init__(self) -> None:
        self._subscriptions: dict[str, MockSubscription] = {}

    def plan_catalog(self) -> dict:
        return {plan.name: plan.as_dict() for plan in list_plans()}

    def create_checkout_session(self, user_id: str, plan_name: str) -> dict:
        plan = get_plan(plan_name)
        return {
            "payment_provider": self.payment_provider,
            "mode": "subscription",
            "checkout_url": f"mock://checkout/{user_id}/{plan.name}",
            "user_id": str(user_id),
            "plan": plan.as_dict(),
            "live_payment": False,
        }

    def create_subscription(self, user_id: str, plan_name: str) -> dict:
        subscription = MockSubscription(user_id=str(user_id), plan=get_plan(plan_name))
        self._subscriptions[subscription.user_id] = subscription
        return subscription.as_dict()

    def handle_webhook(self, event: dict) -> dict:
        event_type = str(event.get("type", "unknown"))
        return {
            "payment_provider": self.payment_provider,
            "received": True,
            "processed": event_type in {"checkout.session.completed", "customer.subscription.updated"},
            "event_type": event_type,
            "live_payment": False,
        }
