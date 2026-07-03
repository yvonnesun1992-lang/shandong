from __future__ import annotations

import json
import re
from pathlib import Path

from product_home.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SENSITIVE_PATTERN = re.compile(r"(secret|token|password|api[_-]?key|authorization|account[_-]?id|order[_-]?id|raw provider)", re.IGNORECASE)


def _safe_name(path: Path) -> str:
    return SENSITIVE_PATTERN.sub("redacted", path.name)


def _safe_json_summary(path: Path) -> str:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "local activity file"
    text = json.dumps(payload, default=str)[:180]
    return SENSITIVE_PATTERN.sub("redacted", text)


def build_recent_activity_summary(limit: int = 10) -> dict:
    candidates: list[Path] = []
    for pattern in ["reports/workflow_runs/*.json", "reports/local_launcher/*.json", "reports/v5_*_report.md"]:
        candidates.extend(PROJECT_ROOT.glob(pattern))
    recent = sorted([path for path in candidates if path.is_file()], key=lambda item: item.stat().st_mtime, reverse=True)[:limit]
    items = []
    for path in recent:
        items.append({
            "name": _safe_name(path),
            "kind": "json" if path.suffix == ".json" else "report",
            "summary": _safe_json_summary(path) if path.suffix == ".json" else "local report",
        })
    return {
        "recent_items": items,
        "latest_system_doctor_placeholder": "Run scripts/system_doctor.py for current status",
        "latest_security_scan_placeholder": "Product home payload safety checks are available",
        "warnings": [],
        **boundary(),
    }
