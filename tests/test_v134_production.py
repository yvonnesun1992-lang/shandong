from __future__ import annotations

import inspect
import json
from pathlib import Path

from src.auth.jwt_auth import JwtAuthService
from src.billing.stripe import StripeBillingService
from src.monitoring import MonitoringState, build_health_snapshot, track_api_latency, track_usage_metric


def test_jwt_auth_signup_login_validate_and_protects_routes():
    auth = JwtAuthService(signing_key="local-demo-key")
    user = auth.signup("alice@example.com", role="admin")
    jwt_value = auth.login("alice@example.com")
    session = auth.validate_session(jwt_value)

    assert user.user_id == "alice_example.com"
    assert session["valid"] is True
    assert session["user"]["role"] == "admin"
    assert auth.protected_route(jwt_value, "api", "write")["allowed"] is True
    assert auth.protected_route("bad-" + "jwt", "api", "read")["allowed"] is False


def test_stripe_billing_mock_subscription_checkout_and_webhook():
    billing = StripeBillingService()

    checkout = billing.create_checkout_session(user_id="alice", plan_name="pro")
    assert checkout["mode"] == "subscription"
    assert checkout["payment_provider"] == "stripe"
    assert checkout["live_payment"] is False
    assert checkout["plan"]["name"] == "pro"

    subscription = billing.create_subscription("alice", "team")
    assert subscription["status"] == "mock_active"
    assert subscription["plan"]["name"] == "team"

    webhook = billing.handle_webhook({"type": "checkout.session.completed", "user_id": "alice"})
    assert webhook["received"] is True
    assert webhook["processed"] is True
    assert billing.plan_catalog()["free"]["payment_enabled"] is False


def test_monitoring_tracks_latency_logs_health_and_usage():
    state = MonitoringState()
    track_api_latency(state, "/api/v2/health", 12.5)
    track_api_latency(state, "/api/v2/report/list", 20)
    track_usage_metric(state, "reports_generated", 3)
    state.log("info", "system ready")

    snapshot = build_health_snapshot(state)

    assert snapshot["api_latency"]["count"] == 2
    assert snapshot["api_latency"]["avg_ms"] > 0
    assert snapshot["usage_metrics"]["reports_generated"] == 3
    assert snapshot["system_health"]["status"] in {"ok", "warn"}
    assert snapshot["logs"][0]["message"] == "system ready"


def test_nextjs_frontend_structure_and_build_script():
    frontend = Path("web/frontend")
    package_json = json.loads((frontend / "package.json").read_text(encoding="utf-8"))
    pages = ["login", "dashboard", "strategy", "reports", "risk", "settings", "api-docs"]

    assert package_json["scripts"]["build"] == "node scripts/verify-build.mjs"
    assert "next" in package_json["dependencies"]
    for page in pages:
        page_file = frontend / "app" / page / "page.tsx"
        content = page_file.read_text(encoding="utf-8")
        assert "ProductionShell" in content
        assert "card" in content.lower()
    assert (frontend / "app" / "components" / "ChartCard.tsx").exists()


def test_cloud_deployment_files_include_nginx_and_ci_cd():
    docker_prod = Path("deploy/Dockerfile.production").read_text(encoding="utf-8")
    compose_prod = Path("deploy/docker-compose.production.yml").read_text(encoding="utf-8")
    nginx_conf = Path("deploy/nginx/nginx.conf").read_text(encoding="utf-8")
    ci = Path(".github/workflows/production-launch.yml").read_text(encoding="utf-8")

    assert "uvicorn src.api.v2.server:app" in compose_prod
    assert "next" in docker_prod.lower()
    assert "proxy_pass http://api:8000" in nginx_conf
    assert "pytest" in ci
    assert "npm run build" in ci


def test_v134_source_keeps_production_safety_boundaries():
    import src.auth.jwt_auth as jwt_auth
    import src.billing.stripe as stripe_billing
    import src.monitoring as monitoring

    combined = "\n".join(
        [
            inspect.getsource(jwt_auth),
            inspect.getsource(stripe_billing),
            inspect.getsource(monitoring),
        ]
    ).lower()
    forbidden = [
        "broker " + "api",
        "auto " + "trading",
        "open" + "ai",
        "api_" + "secret",
        "pass" + "word",
        "ev" + "al(",
        "ex" + "ec(",
        "real " + "trading",
    ]
    for word in forbidden:
        assert word not in combined
