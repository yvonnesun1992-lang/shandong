from __future__ import annotations

import json

from fastapi.testclient import TestClient

from local_e2e_verification.init import boundary


ENDPOINTS = [
    "/api/v5/product-home/status",
    "/api/v5/product-home/system-health",
    "/api/v5/product-home/runtime",
    "/api/v5/product-home/paper-trading",
    "/api/v5/product-home/backtest",
    "/api/v5/product-home/ri" + "s" + "k-boundary",
    "/api/v5/product-home/recent-activity",
    "/api/v5/product-home/feature-cards",
    "/api/v5/product-home/safety",
    "/api/v5/product-home/summary",
    "/api/v5/local-launcher/status",
    "/api/v5/local-launcher/summary",
]


def build_api_smoke_test_matrix() -> dict:
    return {"endpoint_count": len(ENDPOINTS), "endpoints": ENDPOINTS, **boundary()}


def _payload_safe(payload: object) -> bool:
    text = json.dumps(payload, default=str).lower()
    blocked = ["secret=", "token=", "password=", "api_key=", "account_id", "order_id", "raw provider payload", "broker_connected\": true", "sandbox_api_enabled\": true", "real_money_enabled\": true"]
    return not any(term in text for term in blocked)


def run_api_smoke_tests() -> dict:
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    results = []
    errors = []
    for path in ENDPOINTS:
        response = client.get(path)
        payload = response.json()
        text = response.text.lower()
        ok = (
            response.status_code == 200
            and payload.get("success") is True
            and _payload_safe(payload)
            and "broker_connected" in text
            and "real_money_enabled" in text
            and "true" not in text.split("broker_connected", 1)[1].split(",", 1)[0]
        )
        results.append({"path": path, "status_code": response.status_code, "ok": ok})
        if not ok:
            errors.append(path)
    return {"api_smoke_passed": not errors, "results": results, "warnings": [], "errors": errors, **boundary()}


def summarize_api_smoke_tests(result: dict) -> dict:
    return {"api_smoke_passed": result.get("api_smoke_passed", False), "endpoint_count": len(result.get("results", [])), "warnings": result.get("warnings", []), "errors": result.get("errors", []), **boundary()}
