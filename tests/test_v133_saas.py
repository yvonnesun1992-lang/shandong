from __future__ import annotations

import inspect
from pathlib import Path

from src.auth import SessionManager, User, login, logout
from src.auth.api_keys import ApiKeyManager
from src.billing import BillingPlan, get_plan, list_plans
from src.core.rbac import RBACPolicy, can_access, require_permission


def test_mock_login_logout_and_session_context():
    manager = SessionManager()
    user = login("alice@example.com", role="admin", session_manager=manager)

    assert isinstance(user, User)
    assert user.user_id == "alice_example.com"
    assert user.role == "admin"
    assert user.is_authenticated is True
    assert manager.current_user().user_id == "alice_example.com"
    assert manager.user_context().report_namespace == "user:alice_example.com:reports"

    logged_out = logout(session_manager=manager)
    assert logged_out is True
    assert manager.current_user() is None


def test_rbac_rules_control_report_dashboard_and_api_access():
    policy = RBACPolicy()

    assert policy.allowed("admin", "report", "write") is True
    assert policy.allowed("user", "report", "write") is True
    assert policy.allowed("viewer", "report", "write") is False
    assert policy.allowed("viewer", "dashboard", "read") is True
    assert can_access(User("v", role="viewer"), "api", "write") is False
    assert require_permission(User("a", role="admin"), "api", "write")["allowed"] is True
    assert require_permission(User("v", role="viewer"), "api", "write")["allowed"] is False


def test_api_key_manager_generates_revokes_limits_and_tracks_usage():
    manager = ApiKeyManager(rate_limit=2)
    user = User("alice", role="user")

    record = manager.generate_key(user, label="local-dev")
    assert record.user_id == "alice"
    assert record.key_id.startswith("mock_")
    assert record.active is True
    assert manager.authenticate(record.key_value)["allowed"] is True
    assert manager.track_usage(record.key_value)["allowed"] is True
    assert manager.track_usage(record.key_value)["allowed"] is True

    limited = manager.track_usage(record.key_value)
    assert limited["allowed"] is False
    assert limited["reason"] == "rate_limit_exceeded"

    assert manager.revoke_key(record.key_id) is True
    assert manager.authenticate(record.key_value)["allowed"] is False


def test_billing_plans_are_simulated_and_non_payment():
    plans = list_plans()
    names = [plan.name for plan in plans]

    assert names == ["free", "pro", "team"]
    assert isinstance(get_plan("pro"), BillingPlan)
    assert get_plan("team").max_users >= get_plan("pro").max_users
    assert all(plan.payment_enabled is False for plan in plans)


def test_web_frontend_structure_exists():
    expected = [
        "web/login.html",
        "web/dashboard.html",
        "web/strategy-center.html",
        "web/report-viewer.html",
        "web/trend.html",
        "web/api-docs.html",
    ]

    for path in expected:
        content = Path(path).read_text(encoding="utf-8")
        assert "Shandong SaaS" in content
        assert "<script" not in content.lower()


def test_saas_user_system_keeps_isolation():
    alice = User("alice@example.com", role="user")
    bob = User("bob@example.com", role="user")

    assert alice.account.user_root.as_posix() == "data/users/alice_example.com"
    assert bob.account.user_root.as_posix() == "data/users/bob_example.com"
    assert alice.account.report_dir != bob.account.report_dir
    assert alice.context.cache_key("dashboard") != bob.context.cache_key("dashboard")


def test_v133_source_keeps_safety_boundaries():
    import src.auth as auth
    import src.auth.api_keys as api_keys
    import src.billing as billing
    import src.core.rbac as rbac

    combined = "\n".join(
        [
            inspect.getsource(auth),
            inspect.getsource(api_keys),
            inspect.getsource(billing),
            inspect.getsource(rbac),
        ]
    ).lower()
    forbidden = [
        "broker " + "api",
        "auto " + "trading",
        "real " + "payments",
        "open" + "ai",
        "api_" + "secret",
        "pass" + "word",
        "ev" + "al(",
        "ex" + "ec(",
        "str" + "ipe",
    ]
    for word in forbidden:
        assert word not in combined
