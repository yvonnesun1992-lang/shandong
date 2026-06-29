from __future__ import annotations

import re
import os
from pathlib import Path

from config.v5_provider_onboarding_config import VALID_PROVIDERS, get_selected_provider
from provider_onboarding import boundary


DEFAULT_V519_REPORT_PATH = Path("reports/v5_19_provider_selection_report.md")


def get_selected_provider_from_v519(report_path: str | Path = DEFAULT_V519_REPORT_PATH) -> str | None:
    path = Path(report_path)
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    match = re.search(r"recommended provider:\s*([a-z0-9_-]+)", text)
    if not match:
        return None
    provider = match.group(1).strip().lower()
    return provider if provider in VALID_PROVIDERS else None


def resolve_selected_provider(report_path: str | Path = DEFAULT_V519_REPORT_PATH, configured_provider: str | None = None) -> dict:
    report_provider = get_selected_provider_from_v519(report_path)
    if report_provider:
        return {"selected_provider": report_provider, "source": "v519_report", **boundary()}
    raw_config = configured_provider if configured_provider is not None else os.getenv("SHANDONG_V5_SELECTED_PROVIDER", "")
    provider = raw_config.strip().lower()
    if provider in VALID_PROVIDERS:
        return {"selected_provider": provider, "source": "config", **boundary()}
    if not raw_config:
        provider = get_selected_provider()
        if provider in VALID_PROVIDERS:
            return {"selected_provider": provider, "source": "config", **boundary()}
    return {"selected_provider": "alpaca", "source": "fallback", **boundary()}


def build_selected_provider_summary(report_path: str | Path = DEFAULT_V519_REPORT_PATH) -> dict:
    resolved = resolve_selected_provider(report_path=report_path)
    return {
        "version": "V5.20",
        "selected_provider": resolved["selected_provider"],
        "source": resolved["source"],
        "notes": [
            "selected provider is resolved from local V5.19 report when available",
            "no provider portal was accessed",
            "no broker or sandbox API was called",
        ],
        **boundary(),
    }
