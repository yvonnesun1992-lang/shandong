from __future__ import annotations

import socket

from config.v5_local_launcher_config import LOCAL_HOSTS, get_local_launcher_status
from local_launcher.init import boundary


def _safe_host(host: str) -> str:
    return host if host in LOCAL_HOSTS else "127.0.0.1"


def is_port_available(host: str, port: int) -> bool:
    checked_host = _safe_host(host)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((checked_host, int(port))) != 0


def suggest_alternative_ports(host: str, start_port: int, count: int = 3) -> list[int]:
    suggestions: list[int] = []
    port = max(1, int(start_port) + 1)
    while len(suggestions) < count and port <= 65535:
        if is_port_available(_safe_host(host), port):
            suggestions.append(port)
        port += 1
    return suggestions


def check_launcher_ports() -> dict:
    status = get_local_launcher_status()
    checks = []
    warnings = []
    for label, host, port in [
        ("backend", status["backend_host"], status["backend_port"]),
        ("frontend", status["frontend_host"], status["frontend_port"]),
    ]:
        available = is_port_available(host, port)
        item = {"name": label, "host": _safe_host(host), "port": port, "available": available}
        if not available:
            alternatives = suggest_alternative_ports(host, port)
            item["suggested_ports"] = alternatives
            warnings.append(f"{label} port {port} is busy; suggested ports: {alternatives}")
        checks.append(item)
    return {"ports_ready": all(item["available"] for item in checks), "checks": checks, "warnings": warnings, **boundary()}
