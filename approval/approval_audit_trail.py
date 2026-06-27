from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_AUDIT_PATH = Path("logs/manual_approval_audit.jsonl")
ALLOWED_EVENTS = {
    "approval_created",
    "approval_reviewed",
    "approval_rejected",
    "approval_expired",
    "real_order_attempt_rejected",
}


class ApprovalAuditTrail:
    def __init__(self, path: str | Path = DEFAULT_AUDIT_PATH) -> None:
        self.path = Path(path)

    def record_approval_event(self, event_type: str, approval_id: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        safe_event = event_type if event_type in ALLOWED_EVENTS else "approval_rejected"
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event_type": safe_event,
            "approval_id": str(approval_id),
            "metadata": _sanitize_metadata(metadata or {}),
            "manual_approval_required": True,
            "auto_approval_enabled": False,
            "real_orders_enabled": False,
            "paper_trading": True,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return payload

    def get_approval_events(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        events: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return events

    def build_approval_audit_summary(self) -> dict[str, Any]:
        events = self.get_approval_events()
        return {
            "event_count": len(events),
            "approval_created": sum(1 for item in events if item.get("event_type") == "approval_created"),
            "approval_reviewed": sum(1 for item in events if item.get("event_type") == "approval_reviewed"),
            "approval_rejected": sum(1 for item in events if item.get("event_type") == "approval_rejected"),
            "approval_expired": sum(1 for item in events if item.get("event_type") == "approval_expired"),
            "real_order_attempts_rejected": sum(1 for item in events if item.get("event_type") == "real_order_attempt_rejected"),
            "manual_approval_required": True,
            "auto_approval_enabled": False,
            "real_orders_enabled": False,
            "paper_trading": True,
        }


def build_approval_audit_summary(path: str | Path = DEFAULT_AUDIT_PATH) -> dict[str, Any]:
    return ApprovalAuditTrail(path=path).build_approval_audit_summary()


def _sanitize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    blocked = {"secret", "token", "password", "api_key", "authorization", "broker_credential", "account_id", "real_order_id"}
    return {str(key): value for key, value in metadata.items() if str(key).lower() not in blocked}
