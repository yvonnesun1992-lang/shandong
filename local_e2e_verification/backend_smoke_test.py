from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from local_e2e_verification.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_backend_smoke_test_plan() -> dict:
    return {
        "dry_run": True,
        "checks": [
            {"name": "server file exists", "ok": (PROJECT_ROOT / "src/api/v2/server.py").exists()},
            {"name": "use TestClient", "ok": True},
        ],
        **boundary(),
    }


def run_backend_smoke_test(dry_run: bool = True) -> dict:
    errors = []
    responses = []
    try:
        from src.api.v2.server import create_v2_api_app

        client = TestClient(create_v2_api_app())
        for path in ["/api/v5/product-home/status", "/api/v5/local-launcher/status"]:
            response = client.get(path)
            payload = response.json()
            text = response.text.lower()
            ok = response.status_code == 200 and payload.get("success") is True and "broker_connected" in text and "real_money_enabled" in text
            responses.append({"path": path, "status_code": response.status_code, "ok": ok})
            if not ok:
                errors.append(path)
    except Exception as exc:
        errors.append(type(exc).__name__)
    return {"backend_smoke_passed": not errors, "dry_run": dry_run, "responses": responses, "warnings": [], "errors": errors, **boundary()}


def summarize_backend_smoke_test(result: dict) -> dict:
    return {"backend_smoke_passed": result.get("backend_smoke_passed", False), "warnings": result.get("warnings", []), "errors": result.get("errors", []), **boundary()}
