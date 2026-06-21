from __future__ import annotations
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_APP = PROJECT_ROOT / "web" / "frontend" / "app"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v30_frontend_pages_and_navigation_exist():
    assert (FRONTEND_APP / "admin" / "page.tsx").exists()
    assert (FRONTEND_APP / "dashboard" / "page.tsx").exists()
    shell = FRONTEND_APP / "components" / "ProductionShell.tsx"
    assert shell.exists()
    source = read(shell)
    for label in ["Dashboard", "Strategy", "Reports", "Risk", "Admin Console", "Settings", "API Docs"]:
        assert label in source
    assert "activePath" in source


def test_v30_reusable_ui_components_exist():
    components = FRONTEND_APP / "components"
    for name in ["StatusBadge.tsx", "MetricCard.tsx", "EmptyState.tsx", "PageHeader.tsx"]:
        path = components / name
        assert path.exists()
        assert "export" in read(path)


def test_v30_admin_console_and_dashboard_are_product_polished():
    admin = read(FRONTEND_APP / "admin" / "page.tsx")
    dashboard = read(FRONTEND_APP / "dashboard" / "page.tsx")

    for phrase in ["System Overview", "API Health", "Database", "Auth & Security", "Workspace", "Plan / Quota", "Deployment", "Release Candidate"]:
        assert phrase in admin
    for phrase in ["Last checked", "EmptyState", "StatusBadge", "MetricCard"]:
        assert phrase in admin
    for phrase in ["Research mode only", "No broker connection", "No auto trading", "Mock billing only", "Local / demo environment"]:
        assert phrase in dashboard
    assert "Admin Console" in dashboard


def test_v30_styles_define_product_shell_cards_badges_and_states():
    styles = read(FRONTEND_APP / "styles.css")
    for selector in [
        ".shell",
        ".sidebar",
        ".nav a.active",
        ".pageHeader",
        ".grid",
        ".card",
        ".badge",
        ".badge-ok",
        ".badge-warning",
        ".badge-error",
        ".emptyState",
        ".button",
    ]:
        assert selector in styles


def test_v30_ui_docs_and_package_notes_exist():
    assert (PROJECT_ROOT / "docs" / "UI_UX_REVIEW.md").exists()
    assert "V3.0" in read(PROJECT_ROOT / "README.md")
    assert "UI / UX Polish" in read(PROJECT_ROOT / "README.md")
    assert "V3.0" in read(PROJECT_ROOT / "REVIEW_PACKAGE.md")


def test_v30_ui_source_keeps_safety_boundaries():
    source = "\n".join(
        read(path)
        for path in [
            FRONTEND_APP / "admin" / "page.tsx",
            FRONTEND_APP / "dashboard" / "page.tsx",
            FRONTEND_APP / "components" / "ProductionShell.tsx",
            FRONTEND_APP / "styles.css",
            PROJECT_ROOT / "docs" / "UI_UX_REVIEW.md",
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
