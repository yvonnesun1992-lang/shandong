from __future__ import annotations

import json

from local_e2e_verification.init import boundary
from local_launcher.launcher_log_manager import build_launcher_log_event, read_recent_launcher_logs, write_launcher_log


def verify_log_write() -> dict:
    event = build_launcher_log_event("v5_41_local_e2e_verification", "ok", {"message": "local verification log"})
    written = write_launcher_log(event)
    text = json.dumps(written, default=str).lower()
    blocked = ["secret=", "token=", "password=", "api_key=", "real_account_id", "real_order_id", "raw provider payload"]
    errors = [term for term in blocked if term in text]
    return {"log_write_passed": not errors, "event": written, "warnings": [], "errors": errors, **boundary()}


def verify_log_read() -> dict:
    logs = read_recent_launcher_logs(limit=5)
    text = json.dumps(logs, default=str).lower()
    blocked = ["secret=", "token=", "password=", "api_key=", "account_id", "order_id", "raw provider payload"]
    errors = [term for term in blocked if term in text]
    return {"log_read_passed": bool(logs) and not errors, "logs": logs, "warnings": [] if logs else ["no logs found"], "errors": errors, **boundary()}


def summarize_log_verification(result: dict) -> dict:
    write = result.get("write", {})
    read = result.get("read", {})
    errors = write.get("errors", []) + read.get("errors", [])
    warnings = write.get("warnings", []) + read.get("warnings", [])
    return {"log_write_passed": write.get("log_write_passed", False), "log_read_passed": read.get("log_read_passed", False), "warnings": warnings, "errors": errors, **boundary()}
