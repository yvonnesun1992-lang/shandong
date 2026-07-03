from __future__ import annotations

from local_run_doctor.init import boundary


def build_frontend_url() -> str:
    return "http://127.0.0.1:3000"


def build_backend_status_url() -> str:
    return "http://127.0.0.1:8000/api/v5/product-home/status"


def diagnose_browser_targets() -> dict:
    frontend_url = build_frontend_url()
    backend_url = build_backend_status_url()
    valid = frontend_url.startswith("http://127.0.0.1:") and backend_url.startswith("http://127.0.0.1:")
    return {
        "frontend_url": frontend_url,
        "backend_status_url": backend_url,
        "browser_targets_valid": valid,
        "localhost_only": True,
        **boundary(),
    }
