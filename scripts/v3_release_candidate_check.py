from __future__ import annotations

import importlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient


RISK_VALUE_PATTERN = re.compile(r"(sk-[A-Za-z0-9]|ghp_[A-Za-z0-9]|xoxb-|-----BEGIN|" + "live_" + "sec" + "ret)", re.IGNORECASE)


def _check(name: str, fn: Callable[[], tuple[bool, str]]) -> dict:
    try:
        ok, message = fn()
    except Exception as exc:
        return {"name": name, "status": "error", "message": type(exc).__name__}
    return {"name": name, "status": "ok" if ok else "error", "message": message}


def _exists(relative_path: str) -> tuple[bool, str]:
    exists = (PROJECT_ROOT / relative_path).exists()
    return exists, f"{relative_path} {'exists' if exists else 'missing'}"


def _api_endpoint(path: str) -> tuple[bool, str]:
    from src.api.v2.server import create_v2_api_app

    response = TestClient(create_v2_api_app()).get(path)
    return response.status_code == 200, f"{path} status {response.status_code}"


def _admin_console_local() -> tuple[bool, str]:
    original_auth_mode = os.environ.get("SHANDONG_AUTH_MODE")
    try:
        os.environ["SHANDONG_AUTH_MODE"] = "local"
        return _api_endpoint("/api/v2/admin/console")
    finally:
        if original_auth_mode is None:
            os.environ.pop("SHANDONG_AUTH_MODE", None)
        else:
            os.environ["SHANDONG_AUTH_MODE"] = original_auth_mode


def _call_check_module(module_name: str, function_name: str) -> tuple[bool, str]:
    module = importlib.import_module(module_name)
    result = getattr(module, function_name)()
    return result.get("success") is True, f"{function_name} success"


def _call_system_doctor() -> tuple[bool, str]:
    from scripts.system_doctor import run_doctor

    result = run_doctor()
    return result.get("overall_status") in {"ok", "warning"}, f"system_doctor {result.get('overall_status')}"


def _no_committed_env() -> tuple[bool, str]:
    return not (PROJECT_ROOT / ".env").exists(), ".env not committed"


def _no_risk_values() -> tuple[bool, str]:
    scan_files = [
        PROJECT_ROOT / ".env.example",
        PROJECT_ROOT / "docker-compose.yml",
        PROJECT_ROOT / "docker-compose.prod.example.yml",
        PROJECT_ROOT / "docs" / "V3_PRODUCT_DEMO_FREEZE.md",
    ]
    for path in scan_files:
        if path.exists() and RISK_VALUE_PATTERN.search(path.read_text(encoding="utf-8", errors="ignore")):
            return False, f"risk value pattern in {path.name}"
    return True, "no risk value patterns"


def _no_external_runtime_patterns() -> tuple[bool, str]:
    blocked = [
        "aws_" + "access_key",
        "google_" + "application_credentials",
        "azure_" + "client",
        "vercel_" + "tok" + "en",
        "place_" + "order",
        "broker " + "api",
        "stripe " + "live",
        "open" + "ai",
    ]
    for root in [PROJECT_ROOT / "src", PROJECT_ROOT / "scripts", PROJECT_ROOT / "web" / "frontend" / "app"]:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix in {".pyc", ".png"}:
                continue
            if path.name in {"health_check.py", "system_doctor.py", "deployment_dry_run_check.py", "v3_release_candidate_check.py"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            if any(marker in text for marker in blocked):
                return False, f"blocked runtime pattern in {path.name}"
    return True, "no blocked runtime patterns"


def run_v3_release_candidate_check() -> dict:
    original_auth_mode = os.environ.get("SHANDONG_AUTH_MODE")
    try:
        os.environ["SHANDONG_AUTH_MODE"] = "local"
        checks = [
            _check("python_environment", lambda: (sys.version_info >= (3, 10), f"python {sys.version_info.major}.{sys.version_info.minor}")),
            _check("backend_api_import", lambda: (bool(importlib.import_module("src.api.v2.server")), "api import ready")),
            _check("api_app_create", lambda: (bool(importlib.import_module("src.api.v2.server").create_v2_api_app()), "api app created")),
            _check("api_health", lambda: _api_endpoint("/api/v2/health")),
            _check("liveness", lambda: _api_endpoint("/api/v2/system/liveness")),
            _check("readiness", lambda: _api_endpoint("/api/v2/system/readiness")),
            _check("security_health", lambda: _api_endpoint("/api/v2/system/security-health")),
            _check("identity_plan", lambda: _api_endpoint("/api/v2/system/identity-plan")),
            _check("observability", lambda: _api_endpoint("/api/v2/system/observability")),
            _check("deployment_dry_run_endpoint", lambda: _api_endpoint("/api/v2/system/deployment-dry-run")),
            _check("admin_console_local", _admin_console_local),
            _check("dashboard_page", lambda: _exists("web/frontend/app/dashboard/page.tsx")),
            _check("admin_page", lambda: _exists("web/frontend/app/admin/page.tsx")),
            _check("login_page", lambda: _exists("web/frontend/app/login/page.tsx")),
            _check("api_docs_page", lambda: _exists("web/frontend/app/api-docs/page.tsx")),
            _check("auth_status_component", lambda: _exists("web/frontend/app/components/AuthStatus.tsx")),
            _check("permission_notice_component", lambda: _exists("web/frontend/app/components/PermissionNotice.tsx")),
            _check("api_client", lambda: _exists("web/frontend/app/lib/apiClient.ts")),
            _check("auth_client", lambda: _exists("web/frontend/app/lib/authClient.ts")),
            _check("sanitize_helper", lambda: _exists("web/frontend/app/lib/sanitize.ts")),
            _check("identity_status_helper", lambda: _exists("web/frontend/app/lib/identityStatus.ts")),
            _check("styles", lambda: _exists("web/frontend/app/styles.css")),
            _check("ui_ux_review_doc", lambda: _exists("docs/UI_UX_REVIEW.md")),
            _check("frontend_api_doc", lambda: _exists("docs/FRONTEND_API_INTEGRATION.md")),
            _check("frontend_auth_doc", lambda: _exists("docs/FRONTEND_AUTH_FLOW.md")),
            _check("identity_plan_doc", lambda: _exists("docs/PRODUCTION_IDENTITY_PLAN.md")),
            _check("observability_plan_doc", lambda: _exists("docs/OBSERVABILITY_PLAN.md")),
            _check("external_deployment_doc", lambda: _exists("docs/EXTERNAL_DEPLOYMENT_DRY_RUN.md")),
            _check("local_demo_guide", lambda: _exists("docs/LOCAL_DEMO_GUIDE.md")),
            _check("v2_architecture_review", lambda: _exists("docs/V2_ARCHITECTURE_REVIEW.md")),
            _check("deployment_dry_run_check", lambda: _call_check_module("scripts.deployment_dry_run_check", "run_deployment_dry_run_check")),
            _check("local_startup_verification", lambda: _call_check_module("scripts.local_startup_verification", "run_local_startup_verification")),
            _check("v2_integration_check", lambda: _call_check_module("scripts.v2_integration_check", "run_v2_integration_check")),
            _check("system_doctor", _call_system_doctor),
            _check("no_committed_env", _no_committed_env),
            _check("no_risk_values", _no_risk_values),
            _check("no_external_runtime_patterns", _no_external_runtime_patterns),
        ]
    finally:
        if original_auth_mode is None:
            os.environ.pop("SHANDONG_AUTH_MODE", None)
        else:
            os.environ["SHANDONG_AUTH_MODE"] = original_auth_mode

    errors = [check for check in checks if check["status"] == "error"]
    return {"success": not errors, "checks": checks, "warnings": [], "errors": errors}


def main() -> int:
    result = run_v3_release_candidate_check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
