from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SENSITIVE_KEYS = {"api_key", "secret", "token", "password", "authorization", "session_id", "raw_key"}


class MonitoringDataReader:
    def __init__(
        self,
        log_path: str | Path = "logs/runtime.jsonl",
        checkpoint_path: str | Path = "data/runtime_state_checkpoint.json",
        soak_report_path: str | Path = "reports/v5_3_soak_test_report.md",
    ) -> None:
        self.log_path = Path(log_path)
        self.checkpoint_path = Path(checkpoint_path)
        self.soak_report_path = Path(soak_report_path)

    def read_runtime_logs(self) -> list[dict]:
        if not self.log_path.exists():
            return []
        events = []
        try:
            for line in self.log_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                if not line.strip():
                    continue
                try:
                    events.append(sanitize_payload(json.loads(line)))
                except json.JSONDecodeError:
                    events.append({"event_type": "LOG_PARSE_WARNING", "message": "unreadable log line"})
        except Exception:
            return []
        return events

    def read_latest_checkpoint(self) -> dict:
        if not self.checkpoint_path.exists():
            return {"available": False, "warnings": ["checkpoint unavailable"]}
        try:
            payload = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
            payload = sanitize_payload(payload)
            payload["available"] = True
            return payload
        except Exception:
            return {"available": False, "warnings": ["checkpoint unreadable"]}

    def read_soak_report(self) -> dict:
        if not self.soak_report_path.exists():
            return {"available": False, "summary": "", "status": "UNKNOWN", "warnings": ["soak report unavailable"]}
        try:
            text = sanitize_text(self.soak_report_path.read_text(encoding="utf-8", errors="ignore"))
            return {
                "available": True,
                "status": _extract_report_status(text),
                "summary": "\n".join(text.splitlines()[:80]),
                "warnings": [],
            }
        except Exception:
            return {"available": False, "summary": "", "status": "UNKNOWN", "warnings": ["soak report unreadable"]}

    def get_recent_events(self, limit: int = 100) -> list[dict]:
        return self.read_runtime_logs()[-int(limit):]

    def get_error_events(self, limit: int = 100) -> list[dict]:
        return _filter_events(self.read_runtime_logs(), {"ERROR"}, limit)

    def get_trade_events(self, limit: int = 100) -> list[dict]:
        return _filter_events(self.read_runtime_logs(), {"TRADE", "ORDER_FILLED"}, limit)

    def get_signal_events(self, limit: int = 100) -> list[dict]:
        return _filter_events(self.read_runtime_logs(), {"SIGNAL", "SIGNAL_GENERATED"}, limit)


def sanitize_payload(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            key_text = str(key)
            if key_text.lower() in SENSITIVE_KEYS:
                continue
            clean[key_text] = sanitize_payload(item)
        return clean
    if isinstance(value, list):
        return [sanitize_payload(item) for item in value]
    if isinstance(value, str):
        return sanitize_text(value)
    return value


def sanitize_text(text: str) -> str:
    clean = str(text)
    for term in SENSITIVE_KEYS:
        clean = clean.replace(term, "[redacted]")
        clean = clean.replace(term.upper(), "[redacted]")
    return clean.replace(str(Path.cwd()), "[workspace]")


def _filter_events(events: list[dict], names: set[str], limit: int) -> list[dict]:
    selected = []
    for event in events:
        event_type = str(event.get("event_type") or event.get("type") or "").upper()
        if event_type in names:
            selected.append(event)
    return selected[-int(limit):]


def _extract_report_status(text: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if "Final verdict" in line:
            for candidate in lines[index + 1 : index + 4]:
                value = candidate.strip().upper()
                if value in {"PASS", "WARNING", "FAIL"}:
                    return value
    if "WARNING" in text:
        return "WARNING"
    if "FAIL" in text:
        return "FAIL"
    if "PASS" in text:
        return "PASS"
    return "UNKNOWN"
