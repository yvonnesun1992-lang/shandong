from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from local_run_doctor.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def diagnose_backend_import() -> dict:
    server_path = PROJECT_ROOT / "src" / "api" / "v2" / "server.py"
    try:
        from src.api.v2.server import create_v2_api_app

        ok = callable(create_v2_api_app)
        errors: list[str] = []
    except Exception as exc:  # pragma: no cover - defensive import guard
        ok = False
        errors = [exc.__class__.__name__]
    return {"server_file_exists": server_path.exists(), "backend_import_ok": ok, "errors": errors, "warnings": [], **boundary()}


def diagnose_backend_testclient() -> dict:
    try:
        from src.api.v2.server import create_v2_api_app

        client = TestClient(create_v2_api_app())
        ok = client is not None
        errors: list[str] = []
    except Exception as exc:  # pragma: no cover - defensive import guard
        ok = False
        errors = [exc.__class__.__name__]
    return {"backend_testclient_ok": ok, "errors": errors, "warnings": [], **boundary()}


def diagnose_backend_status_endpoint() -> dict:
    try:
        from src.api.v2.server import create_v2_api_app

        client = TestClient(create_v2_api_app())
        product = client.get("/api/v5/product-home/status")
        launcher = client.get("/api/v5/local-launcher/status")
        product_ok = product.status_code == 200 and product.json().get("success") is True
        launcher_ok = launcher.status_code == 200 and launcher.json().get("success") is True
        errors: list[str] = []
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        product_ok = False
        launcher_ok = False
        errors = [exc.__class__.__name__]
    return {
        "product_home_status_ok": product_ok,
        "local_launcher_status_ok": launcher_ok,
        "errors": errors,
        "warnings": [],
        **boundary(),
    }


def build_backend_start_command() -> str:
    return "python -m uvicorn src.api.v2.server:create_v2_api_app --factory --host 127.0.0.1 --port 8000"


def summarize_backend_diagnosis() -> dict:
    imported = diagnose_backend_import()
    testclient = diagnose_backend_testclient()
    status = diagnose_backend_status_endpoint()
    errors = imported.get("errors", []) + testclient.get("errors", []) + status.get("errors", [])
    warnings = imported.get("warnings", []) + testclient.get("warnings", []) + status.get("warnings", [])
    ready = (
        imported["server_file_exists"]
        and imported["backend_import_ok"]
        and testclient["backend_testclient_ok"]
        and status["product_home_status_ok"]
        and status["local_launcher_status_ok"]
    )
    return {
        "backend_ready": ready,
        "backend_import_ok": imported["backend_import_ok"],
        "backend_testclient_ok": testclient["backend_testclient_ok"],
        "product_home_status_ok": status["product_home_status_ok"],
        "local_launcher_status_ok": status["local_launcher_status_ok"],
        "backend_start_command": build_backend_start_command(),
        "warnings": warnings,
        "errors": errors,
        **boundary(),
    }
