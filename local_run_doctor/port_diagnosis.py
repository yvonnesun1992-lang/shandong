from __future__ import annotations

import socket

from local_run_doctor.init import boundary


def check_local_port(host: str, port: int) -> dict:
    if host not in {"127.0.0.1", "localhost"}:
        return {"host": host, "port": port, "open": False, "localhost_only": False, "warnings": ["non-local host blocked"], **boundary()}
    open_ = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        open_ = sock.connect_ex((host, int(port))) == 0
    return {"host": host, "port": int(port), "open": open_, "localhost_only": True, "warnings": [], **boundary()}


def diagnose_default_ports() -> dict:
    frontend = check_local_port("127.0.0.1", 3000)
    backend = check_local_port("127.0.0.1", 8000)
    suggestions = suggest_port_fix({"frontend_port_open": frontend["open"], "backend_port_open": backend["open"]})["suggestions"]
    return {
        "frontend_port": 3000,
        "backend_port": 8000,
        "frontend_port_open": frontend["open"],
        "backend_port_open": backend["open"],
        "frontend_likely_running": frontend["open"],
        "backend_likely_running": backend["open"],
        "suggestions": suggestions,
        **boundary(),
    }


def suggest_port_fix(diagnosis: dict) -> dict:
    suggestions = []
    if not diagnosis.get("frontend_port_open", False):
        suggestions.append("Start the frontend dev server on 127.0.0.1:3000.")
    if not diagnosis.get("backend_port_open", False):
        suggestions.append("Start the backend API server on 127.0.0.1:8000.")
    return {"suggestions": suggestions or ["Default local ports look open."], **boundary()}
