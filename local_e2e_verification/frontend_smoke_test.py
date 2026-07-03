from __future__ import annotations

from pathlib import Path

from local_e2e_verification.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_frontend_smoke_test_plan() -> dict:
    return {"dry_run": True, "frontend_file": "web/frontend/app/page.tsx", **boundary()}


def verify_frontend_files() -> dict:
    checks = []
    page = PROJECT_ROOT / "web/frontend/app/page.tsx"
    api_client = PROJECT_ROOT / "web/frontend/app/lib/apiClient.ts"
    shell = PROJECT_ROOT / "web/frontend/app/components/ProductionShell.tsx"
    page_text = page.read_text(encoding="utf-8") if page.exists() else ""
    api_text = api_client.read_text(encoding="utf-8") if api_client.exists() else ""
    shell_text = shell.read_text(encoding="utf-8") if shell.exists() else ""
    required = [
        ("page exists", page.exists()),
        ("Shandong Quant System", "Shandong Quant System" in page_text),
        ("Local-first paper trading and research dashboard", "Local-first paper trading and research dashboard" in page_text),
        ("No real broker connected", "No real broker connected" in page_text),
        ("No real money", "No real money" in page_text),
        ("No order submission", "No order submission" in page_text),
        ("product home helpers", "fetchV5ProductHomeSummary" in api_text),
        ("navigation Home", "Home" in shell_text),
        ("navigation V5 Product Home", "V5 Product Home" in shell_text),
        ("navigation V5 Local Launcher", "V5 Local Launcher" in shell_text),
    ]
    checks = [{"name": name, "ok": ok} for name, ok in required]
    errors = [item["name"] for item in checks if not item["ok"]]
    return {"frontend_smoke_passed": not errors, "checks": checks, "warnings": [], "errors": errors, **boundary()}


def summarize_frontend_smoke_test(result: dict) -> dict:
    return {"frontend_smoke_passed": result.get("frontend_smoke_passed", False), "warnings": result.get("warnings", []), "errors": result.get("errors", []), **boundary()}
