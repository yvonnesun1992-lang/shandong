from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_pricing_page_and_plan_card_exist():
    page = ROOT / "web/frontend/app/pricing/page.tsx"
    card = ROOT / "web/frontend/app/components/PricingPlanCard.tsx"

    assert page.exists()
    assert card.exists()

    page_text = page.read_text(encoding="utf-8")
    card_text = card.read_text(encoding="utf-8")

    for phrase in [
        "Pricing & Packaging",
        "Free Demo",
        "Research Pro",
        "Team Workspace",
        "Enterprise Planned",
        "Billing mock only",
        "No real payment",
        "No Stripe",
        "live",
        "No credit card collection",
        "No real subscription",
    ]:
        assert phrase in page_text

    for phrase in ["Plan name", "Status", "Price label", "Feature list", "CTA", "Demo only", "Contact planned", "Not payment button"]:
        assert phrase in card_text

    forbidden_cta = ["Pay now", "Checkout", "Stripe checkout"]
    for phrase in forbidden_cta:
        assert phrase not in page_text
        assert phrase not in card_text


def test_pricing_plan_endpoint_is_safe():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    response = client.get("/api/v2/system/pricing-plan")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    pricing = payload["data"]["pricing"]
    assert pricing["billing_mode"] == "mock"
    assert pricing["real_payment_enabled"] is False
    assert pricing["stripe_live_enabled"] is False
    assert pricing["commercial_ready"] is False
    assert [plan["name"] for plan in pricing["plans"]] == ["Free Demo", "Research Pro", "Team Workspace", "Enterprise Planned"]

    lowered = json.dumps(payload, sort_keys=True).lower()
    for forbidden in [
        "secret",
        "token",
        "password",
        "api_key",
        "payment method",
        "card number",
        "credit card number",
        "stripe key",
        "/users/apple",
    ]:
        assert forbidden not in lowered


def test_frontend_api_nav_and_admin_commercial_readiness_surface():
    api_client = read_text("web/frontend/app/lib/apiClient.ts")
    shell = read_text("web/frontend/app/components/ProductionShell.tsx")
    admin_page = read_text("web/frontend/app/admin/page.tsx")

    assert "fetchPricingPlan" in api_client
    assert "/api/v2/system/pricing-plan" in api_client
    assert "Pricing" in shell
    assert "/pricing" in shell
    assert "Commercial Readiness" in admin_page
    assert "Pricing page: available" in admin_page
    assert "Billing mode: mock" in admin_page
    assert "Real payment: not enabled" in admin_page
    assert "Stripe" in admin_page
    assert "live'}: not connected" in admin_page
    assert "Subscription lifecycle: planned" in admin_page
    assert "Customer billing: not connected" in admin_page


def test_commercial_readiness_docs_and_package_updates_exist():
    docs = read_text("docs/COMMERCIAL_READINESS.md")
    readme = read_text("README.md")
    review = read_text("REVIEW_PACKAGE.md")

    for phrase in [
        "Current Commercial State",
        "Packaging Hypothesis",
        "What Needs To Be Done Before Charging Money",
        "Not Implemented Yet",
        "no real checkout",
        "no Stripe live",
        "no credit card collection",
        "no invoice",
        "no subscription lifecycle",
        "no paid customer onboarding",
    ]:
        assert phrase in docs

    assert "V3.9" in readme
    assert "Pricing / Packaging / Commercial Readiness" in readme
    assert "Pricing Page" in readme
    assert "Pricing endpoint" in readme
    assert "No real payment enabled" in readme
    assert "V3.9" in review
    assert "pricing / packaging / commercial readiness" in review.lower()


def test_v39_runtime_boundaries():
    runtime_files = [
        "src/api/v2/server.py",
        "web/frontend/app/pricing/page.tsx",
        "web/frontend/app/components/PricingPlanCard.tsx",
        "web/frontend/app/components/ProductionShell.tsx",
        "web/frontend/app/admin/page.tsx",
        "web/frontend/app/lib/apiClient.ts",
    ]
    combined = "\n".join(read_text(path) for path in runtime_files).lower()

    forbidden = [
        "pay now",
        "credit card collection enabled",
        "save card",
        "broker api",
        "auto order",
        "place_order",
        "openai",
        "oauth client",
        "production secret",
        "eval(",
        "exec(",
    ]
    for pattern in forbidden:
        assert pattern not in combined
