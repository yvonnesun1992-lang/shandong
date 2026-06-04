from __future__ import annotations

import copy
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SETTINGS_PATH = PROJECT_ROOT / "config" / "settings.json"

DEFAULT_SETTINGS = {
    "cache": {
        "enabled": True,
        "max_age_days": 7,
    },
    "reports": {
        "daily_report_dir": "reports/daily",
        "backtest_report_dir": "reports/backtests",
        "workflow_run_dir": "reports/workflow_runs",
    },
    "paper_trading": {
        "initial_cash": 100000.0,
    },
    "dashboard": {
        "default_market": "us",
        "show_disclaimer": True,
    },
    "workflow": {
        "min_success_symbols": 1,
    },
}

SENSITIVE_KEYS = {"api_key", "apikey", "secret", "password", "token"}


def _default_settings() -> dict:
    return copy.deepcopy(DEFAULT_SETTINGS)


def _settings_path(path: str | Path) -> Path:
    raw_path = Path(path)
    if ".." in raw_path.parts:
        raise ValueError("Settings path cannot contain path traversal.")
    resolved = raw_path.resolve()
    if resolved.name != "settings.json" or resolved.parent.name != "config":
        raise ValueError("Settings can only be read from or written to config/settings.json.")
    return resolved


def _contains_sensitive_key(value) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized in SENSITIVE_KEYS or normalized.endswith("_secret") or normalized.endswith("_token"):
                return True
            if _contains_sensitive_key(item):
                return True
    elif isinstance(value, list):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def validate_settings(settings: dict) -> dict:
    """Validate settings and return a normalized settings dictionary."""
    if not isinstance(settings, dict):
        raise ValueError("Settings must be a JSON object.")
    if _contains_sensitive_key(settings):
        raise ValueError("Settings must not contain API keys, secrets, passwords, or tokens.")

    normalized = _default_settings()
    for section, defaults in DEFAULT_SETTINGS.items():
        raw_section = settings.get(section, {})
        if raw_section is None:
            raw_section = {}
        if not isinstance(raw_section, dict):
            raise ValueError(f"Settings section '{section}' must be an object.")
        normalized[section].update(raw_section)

    if not isinstance(normalized["cache"]["enabled"], bool):
        raise ValueError("cache.enabled must be a boolean.")
    max_age_days = normalized["cache"]["max_age_days"]
    if not isinstance(max_age_days, int) or isinstance(max_age_days, bool) or max_age_days <= 0:
        raise ValueError("cache.max_age_days must be a positive integer.")

    initial_cash = normalized["paper_trading"]["initial_cash"]
    if not isinstance(initial_cash, (int, float)) or isinstance(initial_cash, bool) or initial_cash <= 0:
        raise ValueError("paper_trading.initial_cash must be a positive number.")
    normalized["paper_trading"]["initial_cash"] = float(initial_cash)

    default_market = str(normalized["dashboard"]["default_market"]).strip().lower()
    if default_market not in {"us", "cn"}:
        raise ValueError("dashboard.default_market must be 'us' or 'cn'.")
    normalized["dashboard"]["default_market"] = default_market

    if not isinstance(normalized["dashboard"]["show_disclaimer"], bool):
        raise ValueError("dashboard.show_disclaimer must be a boolean.")

    min_success_symbols = normalized["workflow"]["min_success_symbols"]
    if (
        not isinstance(min_success_symbols, int)
        or isinstance(min_success_symbols, bool)
        or min_success_symbols <= 0
    ):
        raise ValueError("workflow.min_success_symbols must be a positive integer.")

    return normalized


def _write_settings(path: Path, settings: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def reset_settings(path: str | Path = DEFAULT_SETTINGS_PATH) -> dict:
    settings_path = _settings_path(path)
    settings = _default_settings()
    _write_settings(settings_path, settings)
    return settings


def load_settings(path: str | Path = DEFAULT_SETTINGS_PATH) -> dict:
    settings_path = _settings_path(path)
    if not settings_path.exists():
        return reset_settings(settings_path)
    try:
        raw_settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid settings JSON in {settings_path.name}: {error}") from error
    return validate_settings(raw_settings)


def save_settings(settings: dict, path: str | Path = DEFAULT_SETTINGS_PATH) -> None:
    settings_path = _settings_path(path)
    normalized = validate_settings(settings)
    _write_settings(settings_path, normalized)


def get_setting(
    section: str,
    key: str,
    default=None,
    path: str | Path = DEFAULT_SETTINGS_PATH,
):
    settings = load_settings(path)
    section_settings = settings.get(section, {})
    if not isinstance(section_settings, dict):
        return default
    return section_settings.get(key, default)


def update_setting(
    section: str,
    key: str,
    value,
    path: str | Path = DEFAULT_SETTINGS_PATH,
) -> dict:
    settings = load_settings(path)
    settings.setdefault(section, {})
    if not isinstance(settings[section], dict):
        raise ValueError(f"Settings section '{section}' must be an object.")
    settings[section][key] = value
    save_settings(settings, path)
    return load_settings(path)
