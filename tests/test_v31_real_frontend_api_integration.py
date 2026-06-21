from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_APP = PROJECT_ROOT / "web" / "frontend" / "app"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v31_frontend_api_client_exists_and_exports_fetchers():
    api_client = FRONTEND_APP / "lib" / "apiClient.ts"
    assert api_client.exists()
    source = read(api_client)
    for name in [
        "getApiBaseUrl",
        "apiGet",
        "fetchAdminConsole",
        "fetchReadiness",
        "fetchLiveness",
        "fetchSecurityHealth",
        "fetchWorkspaceHealth",
        "fetchBillingHealth",
    ]:
        assert name in source
    assert "NEXT_PUBLIC_API_BASE_URL" in source
    assert "http://localhost:8000" in source


def test_v31_admin_console_and_dashboard_use_api_client_with_fallbacks():
    admin = read(FRONTEND_APP / "admin" / "page.tsx")
    dashboard = read(FRONTEND_APP / "dashboard" / "page.tsx")

    assert "fetchAdminConsole" in admin
    assert "fallbackConsole" in admin
    assert "LoadingState" in admin
    assert "ErrorState" in admin
    assert "fetchReadiness" in dashboard
    assert "fetchLiveness" in dashboard
    assert "fallbackDashboard" in dashboard
    assert "Admin Console" in dashboard


def test_v31_frontend_state_components_exist_or_are_equivalent():
    components = FRONTEND_APP / "components"
    for name in ["LoadingState.tsx", "ErrorState.tsx", "StatusBadge.tsx", "MetricCard.tsx"]:
        path = components / name
        assert path.exists()
        assert "export" in read(path)


def test_v31_sanitizer_exists_and_filters_sensitive_markers():
    sanitizer = FRONTEND_APP / "lib" / "sanitize.ts"
    assert sanitizer.exists()
    source = read(sanitizer)
    assert "sanitizeText" in source
    assert "sanitizePayload" in source
    assert "SENSITIVE_KEYS" in source
    assert "LOCAL_PATH_PATTERN" in source
    assert "DB_FILE_PATTERN" in source


def test_v31_docs_and_package_notes_exist():
    assert (PROJECT_ROOT / "docs" / "FRONTEND_API_INTEGRATION.md").exists()
    assert "V3.1" in read(PROJECT_ROOT / "README.md")
    assert "Real Frontend API Integration" in read(PROJECT_ROOT / "README.md")
    assert "V3.1" in read(PROJECT_ROOT / "REVIEW_PACKAGE.md")


def test_v31_frontend_source_keeps_safety_boundaries():
    source = "\n".join(
        read(path)
        for path in [
            FRONTEND_APP / "lib" / "apiClient.ts",
            FRONTEND_APP / "lib" / "sanitize.ts",
            FRONTEND_APP / "admin" / "page.tsx",
            FRONTEND_APP / "dashboard" / "page.tsx",
            FRONTEND_APP / "components" / "LoadingState.tsx",
            FRONTEND_APP / "components" / "ErrorState.tsx",
            PROJECT_ROOT / "docs" / "FRONTEND_API_INTEGRATION.md",
        ]
    ).lower()
    forbidden = [
        "broker " + "api",
        "auto" + "order",
        "place_" + "order",
        "open" + "ai",
        "stripe " + "live",
        "live_" + "secret",
        "password=",
        "token=",
        "api_key=",
        "raw_key",
        "session_id",
        "authorization",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in source
