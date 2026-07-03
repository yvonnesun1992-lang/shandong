from __future__ import annotations

import json
import re

from config.v5_local_launcher_config import get_local_launcher_status
from local_launcher.init import boundary


FALSE_KEYS = [
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
    "balance_read_enabled",
    "position_read_enabled",
    "order_preview_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def validate_local_launcher_safety(payload: object) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings: list[dict] = []
    if isinstance(payload, dict):
        if payload.get("local_launcher_only") is False:
            findings.append({"kind": "boundary", "match": "local_launcher_only_false"})
        if payload.get("localhost_only") is False:
            findings.append({"kind": "boundary", "match": "localhost_only_false"})
        for key in FALSE_KEYS:
            if payload.get(key) is True:
                findings.append({"kind": "boundary", "match": key})
    blocked_terms = [
        "raw provider payload",
        "real_account_id",
        "real_order_id",
        "paper-api.",
        "api.alpaca.",
        "https://sandbox",
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
    ]
    for term in blocked_terms:
        if term in text:
            findings.append({"kind": "blocked-term", "match": term})
    for pattern in [
        r"sk-[a-z0-9]",
        r"api[_-]?key\s*[:=]\s*[a-z0-9]",
        r"secret\s*[:=]\s*[a-z0-9]",
        r"token\s*[:=]\s*[a-z0-9]",
        r"password\s*[:=]\s*[a-z0-9]",
        r"authorization\s*[:=]\s*[a-z0-9]",
    ]:
        if re.search(pattern, text, re.IGNORECASE):
            findings.append({"kind": "sensitive-pattern", "match": "credential-like-value"})
            break
    if "http://" in text or "https://" in text:
        for match in re.findall(r"https?://[^\\s\"']+", text):
            if "127.0.0.1" not in match and "localhost" not in match:
                findings.append({"kind": "external-url", "match": "non-local-url"})
                break
    return {"safe": not findings, "findings": findings, **boundary()}


def build_local_launcher_safety_summary() -> dict:
    status = get_local_launcher_status()
    safety = validate_local_launcher_safety(status)
    return {"safe": safety["safe"], "findings": safety["findings"], "status": status, **boundary()}
