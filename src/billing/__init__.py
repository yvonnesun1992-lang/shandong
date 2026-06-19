from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BillingPlan:
    name: str
    monthly_price_usd: int
    max_users: int
    max_reports_per_month: int
    api_rate_limit: int
    payment_enabled: bool = False

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "monthly_price_usd": self.monthly_price_usd,
            "max_users": self.max_users,
            "max_reports_per_month": self.max_reports_per_month,
            "api_rate_limit": self.api_rate_limit,
            "payment_enabled": self.payment_enabled,
        }


PLANS = {
    "free": BillingPlan("free", monthly_price_usd=0, max_users=1, max_reports_per_month=10, api_rate_limit=100),
    "pro": BillingPlan("pro", monthly_price_usd=29, max_users=3, max_reports_per_month=200, api_rate_limit=1000),
    "team": BillingPlan("team", monthly_price_usd=99, max_users=10, max_reports_per_month=1000, api_rate_limit=5000),
}


def list_plans() -> list[BillingPlan]:
    return [PLANS["free"], PLANS["pro"], PLANS["team"]]


def get_plan(name: str) -> BillingPlan:
    return PLANS.get(str(name).lower(), PLANS["free"])
