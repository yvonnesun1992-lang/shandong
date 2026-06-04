from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Callable

import pandas as pd

from src.config.settings import DEFAULT_SETTINGS_PATH, load_settings, validate_settings
from src.data.data_quality import validate_ohlcv_data
from src.data.price_cache import DEFAULT_PRICE_CACHE_DIR, list_cached_symbols
from src.data.watchlist_manager import DEFAULT_WATCHLIST_PATH, load_watchlists
from src.workflows.run_log import DEFAULT_WORKFLOW_RUN_DIR, list_workflow_run_logs


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_DIRECTORIES = [
    PROJECT_ROOT / "config",
    PROJECT_ROOT / "data" / "sample",
    PROJECT_ROOT / "data" / "cache",
    PROJECT_ROOT / "reports" / "backtests",
    PROJECT_ROOT / "reports" / "daily",
    PROJECT_ROOT / "reports" / "workflow_runs",
]
REQUIRED_FILES = [
    DEFAULT_SETTINGS_PATH,
    DEFAULT_WATCHLIST_PATH,
    PROJECT_ROOT / "config" / "paper_portfolio.json",
    PROJECT_ROOT / "data" / "sample" / "us_NVDA.csv",
    PROJECT_ROOT / "data" / "sample" / "cn_300308.csv",
]
SAMPLE_DATA_FILES = [
    PROJECT_ROOT / "data" / "sample" / "us_NVDA.csv",
    PROJECT_ROOT / "data" / "sample" / "cn_300308.csv",
]
REPORT_DIRECTORIES = [
    PROJECT_ROOT / "reports" / "backtests",
    PROJECT_ROOT / "reports" / "daily",
    PROJECT_ROOT / "reports" / "workflow_runs",
]
CODE_SCAN_DIRECTORIES = [
    PROJECT_ROOT / "src",
    PROJECT_ROOT / "app",
    PROJECT_ROOT / "scripts",
]
FORBIDDEN_KEYWORDS = [
    "IBKR",
    "Alpaca",
    "Robinhood",
    "broker order",
    "place_order",
    "real trade",
    "api_key",
    "secret",
    "password",
    "token",
    "OpenAI API",
    "AI prediction",
]
IGNORED_SECURITY_CONTEXTS = [
    "SENSITIVE_KEYS",
    "forbidden",
    "must not contain",
    "no api key",
    "no broker",
    "no auto",
    "不连接",
    "不自动",
    "不包含",
    "不调用",
    "不保存",
    "不使用",
    "不会连接",
    "不会产生",
    "只保存",
    "import secrets",
    "secrets.token_hex",
]


def _check(name: str, status: str, message: str, details: dict | None = None) -> dict:
    return {
        "name": name,
        "status": status,
        "message": message,
        "details": details or {},
    }


def _relative_key(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def _safe_check(check_func: Callable[[], dict]) -> dict:
    try:
        return check_func()
    except Exception as error:
        return _check(
            getattr(check_func, "__name__", "unknown_check"),
            "error",
            str(error),
            {"error_type": type(error).__name__},
        )


def _json_file_status(path: Path) -> tuple[str, str]:
    if not path.exists():
        return "warning", "missing"
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "error", "invalid_json"
    return "ok", "valid_json"


def check_required_directories() -> dict:
    missing = [str(path.relative_to(PROJECT_ROOT)) for path in REQUIRED_DIRECTORIES if not path.is_dir()]
    if missing:
        return _check(
            "required_directories",
            "warning",
            "Some required local directories are missing.",
            {"missing": missing},
        )
    return _check("required_directories", "ok", "All required local directories exist.")


def check_required_files() -> dict:
    details = {}
    statuses = []
    for path in REQUIRED_FILES:
        relative = _relative_key(path)
        if not path.exists():
            details[relative] = "missing"
            statuses.append("warning")
            continue
        if path.suffix.lower() == ".json":
            status, message = _json_file_status(path)
            details[relative] = message
            statuses.append(status)
            continue
        if path.suffix.lower() == ".csv":
            try:
                data = pd.read_csv(path)
                report = validate_ohlcv_data(data)
            except Exception as error:
                details[relative] = f"invalid_csv: {error}"
                statuses.append("error")
                continue
            if report["errors"]:
                details[relative] = {"errors": report["errors"]}
                statuses.append("error")
            else:
                details[relative] = "valid_csv"
                statuses.append("ok")
            continue
        details[relative] = "exists"
        statuses.append("ok")

    if "error" in statuses:
        return _check("required_files", "error", "Some required files are invalid.", details)
    if "warning" in statuses:
        return _check("required_files", "warning", "Some required files are missing.", details)
    return _check("required_files", "ok", "All required files exist and basic validation passed.", details)


def check_settings_health() -> dict:
    existed_before = DEFAULT_SETTINGS_PATH.exists()
    try:
        settings = load_settings(DEFAULT_SETTINGS_PATH)
        validate_settings(settings)
    except ValueError as error:
        return _check("settings", "error", str(error), {"path": str(DEFAULT_SETTINGS_PATH)})
    status = "ok" if existed_before else "warning"
    message = "settings.json is valid." if existed_before else "settings.json was missing and default settings were created."
    return _check("settings", status, message, {"path": str(DEFAULT_SETTINGS_PATH)})


def check_watchlist_health() -> dict:
    try:
        watchlists = load_watchlists()
    except ValueError as error:
        return _check("watchlists", "error", str(error), {"path": str(DEFAULT_WATCHLIST_PATH)})

    errors = []
    warnings = []
    for default_name in ["us_default", "cn_default"]:
        if default_name not in watchlists:
            errors.append(f"Missing {default_name}.")
    for name, symbols in watchlists.items():
        if not isinstance(symbols, list) or not all(isinstance(symbol, str) for symbol in symbols):
            errors.append(f"Watchlist {name} must be list[str].")
        if isinstance(symbols, list) and not symbols:
            warnings.append(f"Watchlist {name} is empty.")

    details = {
        "watchlist_count": len(watchlists),
        "watchlists": {name: len(symbols) for name, symbols in watchlists.items()},
        "warnings": warnings,
        "errors": errors,
    }
    if errors:
        return _check("watchlists", "error", "Watchlist configuration has errors.", details)
    if warnings:
        return _check("watchlists", "warning", "Watchlist configuration has warnings.", details)
    return _check("watchlists", "ok", "Watchlist configuration is valid.", details)


def check_sample_data_health() -> dict:
    details = {}
    statuses = []
    for path in SAMPLE_DATA_FILES:
        relative = _relative_key(path)
        if not path.exists():
            details[relative] = {"errors": ["File is missing."]}
            statuses.append("error")
            continue
        try:
            data = pd.read_csv(path)
            report = validate_ohlcv_data(data, min_rows=120)
        except Exception as error:
            details[relative] = {"errors": [str(error)]}
            statuses.append("error")
            continue
        details[relative] = report
        if report["errors"]:
            statuses.append("error")
        elif report["warnings"]:
            statuses.append("warning")
        else:
            statuses.append("ok")

    if "error" in statuses:
        return _check("sample_data", "error", "Sample data has validation errors.", details)
    if "warning" in statuses:
        return _check("sample_data", "warning", "Sample data has validation warnings.", details)
    return _check("sample_data", "ok", "Sample data is valid.", details)


def check_cache_health() -> dict:
    cache_dir = DEFAULT_PRICE_CACHE_DIR
    if not cache_dir.exists():
        return _check("cache", "warning", "Cache directory is missing.", {"path": str(cache_dir)})

    abnormal_files = []
    for path in cache_dir.iterdir():
        if path.name == ".gitkeep":
            continue
        if path.is_file() and path.suffix.lower() != ".csv":
            abnormal_files.append(path.name)

    try:
        cached_symbols = list_cached_symbols(cache_dir)
    except ValueError as error:
        return _check("cache", "error", str(error), {"path": str(cache_dir)})

    details = {
        "path": str(cache_dir),
        "cache_file_count": int(len(list(cache_dir.glob("*.csv")))),
        "cached_symbol_count": int(len(cached_symbols)),
        "abnormal_files": abnormal_files,
    }
    if abnormal_files:
        return _check("cache", "warning", "Cache directory contains non-CSV files.", details)
    return _check("cache", "ok", "Cache directory is readable.", details)


def check_reports_health() -> dict:
    details = {}
    statuses = []
    for directory in REPORT_DIRECTORIES:
        relative = str(directory.relative_to(PROJECT_ROOT))
        if not directory.exists():
            details[relative] = {"status": "missing"}
            statuses.append("warning")
            continue
        invalid_json = []
        json_count = 0
        for path in directory.glob("*.json"):
            json_count += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                invalid_json.append(path.name)
        details[relative] = {
            "json_count": json_count,
            "invalid_json": invalid_json,
        }
        statuses.append("error" if invalid_json else "ok")

    if "error" in statuses:
        return _check("reports", "error", "Some report JSON files are damaged.", details)
    if "warning" in statuses:
        return _check("reports", "warning", "Some report directories are missing.", details)
    return _check("reports", "ok", "Report directories are readable.", details)


def check_workflow_logs_health() -> dict:
    if not DEFAULT_WORKFLOW_RUN_DIR.exists():
        return _check(
            "workflow_logs",
            "warning",
            "Workflow run directory is missing.",
            {"path": str(DEFAULT_WORKFLOW_RUN_DIR)},
        )
    try:
        logs = list_workflow_run_logs(DEFAULT_WORKFLOW_RUN_DIR)
    except ValueError as error:
        return _check("workflow_logs", "error", str(error), {"path": str(DEFAULT_WORKFLOW_RUN_DIR)})
    return _check(
        "workflow_logs",
        "ok",
        "Workflow run logs are readable.",
        {"path": str(DEFAULT_WORKFLOW_RUN_DIR), "log_count": int(len(logs))},
    )


def _is_ignored_security_line(line: str) -> bool:
    lower_line = line.lower()
    return any(context.lower() in lower_line for context in IGNORED_SECURITY_CONTEXTS)


def check_security_boundary() -> dict:
    findings = []
    for directory in CODE_SCAN_DIRECTORIES:
        if not directory.exists():
            continue
        for path in directory.rglob("*.py"):
            if path.resolve() == Path(__file__).resolve():
                continue
            text = path.read_text(encoding="utf-8")
            for line_number, line in enumerate(text.splitlines(), start=1):
                if _is_ignored_security_line(line):
                    continue
                for keyword in FORBIDDEN_KEYWORDS:
                    if keyword.lower() in line.lower():
                        findings.append(
                            {
                                "file": str(path.relative_to(PROJECT_ROOT)),
                                "line": line_number,
                                "keyword": keyword,
                            }
                        )

    details = {
        "scanned_directories": [str(path.relative_to(PROJECT_ROOT)) for path in CODE_SCAN_DIRECTORIES],
        "findings": findings,
    }
    if findings:
        return _check(
            "security_boundary",
            "error",
            "Potential broker, order, secret, or AI API risk keywords were found in runtime code.",
            details,
        )
    return _check(
        "security_boundary",
        "ok",
        "No real broker connection, auto order, credential storage, or AI API call risk found in runtime code.",
        details,
    )


def run_system_health_check() -> dict:
    check_functions = [
        check_required_directories,
        check_required_files,
        check_settings_health,
        check_watchlist_health,
        check_sample_data_health,
        check_cache_health,
        check_reports_health,
        check_workflow_logs_health,
        check_security_boundary,
    ]
    checks = [_safe_check(check_func) for check_func in check_functions]
    ok_count = sum(1 for check in checks if check["status"] == "ok")
    warning_count = sum(1 for check in checks if check["status"] == "warning")
    error_count = sum(1 for check in checks if check["status"] == "error")
    if error_count:
        overall_status = "error"
    elif warning_count:
        overall_status = "warning"
    else:
        overall_status = "ok"
    return {
        "overall_status": overall_status,
        "checks": checks,
        "ok_count": ok_count,
        "warning_count": warning_count,
        "error_count": error_count,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def health_check_to_dataframe(result: dict) -> pd.DataFrame:
    checks = result.get("checks", [])
    rows = [
        {
            "name": check.get("name"),
            "status": check.get("status"),
            "message": check.get("message"),
        }
        for check in checks
    ]
    return pd.DataFrame(rows, columns=["name", "status", "message"])
