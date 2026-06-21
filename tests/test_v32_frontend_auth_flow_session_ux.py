from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_APP = PROJECT_ROOT / "web" / "frontend" / "app"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v32_auth_client_exists_and_exports_demo_session_helpers():
    auth_client = FRONTEND_APP / "lib" / "authClient.ts"
    assert auth_client.exists()
    source = read(auth_client)
    for name in [
        "loginDemoUser",
        "logoutDemoUser",
        "getStoredSession",
        "getStoredRole",
        "clearStoredSession",
        "isDemoAuthenticated",
    ]:
        assert name in source
    assert "/api/v2/auth/login" in source
    assert "demo_admin" in source
    assert "demo_user" in source
    assert "demo_viewer" in source


def test_v32_api_client_supports_session_header_without_page_exposure():
    api_client = read(FRONTEND_APP / "lib" / "apiClient.ts")
    admin = read(FRONTEND_APP / "admin" / "page.tsx")
    dashboard = read(FRONTEND_APP / "dashboard" / "page.tsx")

    assert "X-Session-ID" in api_client
    assert "getStoredSession" in api_client
    assert "Authentication required" in api_client
    assert "Permission denied" in api_client
    assert "Session expired or unavailable" in api_client
    assert "X-Session-ID" not in admin
    assert "X-Session-ID" not in dashboard


def test_v32_login_page_and_auth_components_exist():
    login = read(FRONTEND_APP / "login" / "page.tsx")
    assert "Demo Login" in login
    assert "Admin" in login
    assert "User" in login
    assert "Viewer" in login
    assert "mock login" in login.lower()
    assert "Password" not in login
    assert "AuthStatus" in login
    assert (FRONTEND_APP / "components" / "AuthStatus.tsx").exists()
    assert (FRONTEND_APP / "components" / "PermissionNotice.tsx").exists()


def test_v32_admin_console_and_dashboard_use_auth_state():
    admin = read(FRONTEND_APP / "admin" / "page.tsx")
    dashboard = read(FRONTEND_APP / "dashboard" / "page.tsx")

    assert "AuthStatus" in admin
    assert "PermissionNotice" in admin
    assert "fetchAdminConsole" in admin
    assert "AuthStatus" in dashboard
    assert "getStoredRole" in dashboard or "AuthStatus" in dashboard
    assert "raw session" not in admin.lower()
    assert "raw session" not in dashboard.lower()


def test_v32_sanitizer_filters_auth_sensitive_markers():
    sanitizer = read(FRONTEND_APP / "lib" / "sanitize.ts")
    for marker in ["secret", "bearer", "X-Session-ID", ".env", "LOCAL_PATH_PATTERN", "DB_FILE_PATTERN"]:
        assert marker in sanitizer
    assert "sanitizeText" in sanitizer
    assert "sanitizePayload" in sanitizer


def test_v32_docs_and_package_notes_exist():
    assert (PROJECT_ROOT / "docs" / "FRONTEND_AUTH_FLOW.md").exists()
    assert "V3.2" in read(PROJECT_ROOT / "README.md")
    assert "Frontend Auth Flow" in read(PROJECT_ROOT / "README.md")
    assert "V3.2" in read(PROJECT_ROOT / "REVIEW_PACKAGE.md")


def test_v32_frontend_source_keeps_safety_boundaries():
    source = "\n".join(
        read(path)
        for path in [
            FRONTEND_APP / "lib" / "authClient.ts",
            FRONTEND_APP / "lib" / "apiClient.ts",
            FRONTEND_APP / "lib" / "sanitize.ts",
            FRONTEND_APP / "login" / "page.tsx",
            FRONTEND_APP / "admin" / "page.tsx",
            FRONTEND_APP / "dashboard" / "page.tsx",
            FRONTEND_APP / "components" / "AuthStatus.tsx",
            FRONTEND_APP / "components" / "PermissionNotice.tsx",
            PROJECT_ROOT / "docs" / "FRONTEND_AUTH_FLOW.md",
        ]
    ).lower()
    forbidden = [
        "broker " + "api",
        "auto" + "order",
        "place_" + "order",
        "open" + "ai",
        "stripe " + "live",
        "password=",
        "token=",
        "api_key=",
        "secret=",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in source
