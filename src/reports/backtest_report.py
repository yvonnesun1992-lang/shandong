from __future__ import annotations

import json
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_BACKTEST_REPORT_DIR = Path(__file__).resolve().parents[2] / "reports" / "backtests"
REPORT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
SENSITIVE_KEYS = {"api_key", "apikey", "secret", "password", "token"}
SUMMARY_COLUMNS = [
    "report_id",
    "created_at",
    "report_type",
    "total_return",
    "annualized_return",
    "max_drawdown",
    "number_of_trades",
    "final_portfolio_value",
]


def _ensure_report_dir(output_dir: str | Path = DEFAULT_BACKTEST_REPORT_DIR) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _validate_safe_name(value: str, field_name: str) -> str:
    if not value or not REPORT_ID_PATTERN.fullmatch(value):
        raise ValueError(f"{field_name} may only contain letters, numbers, underscores, and hyphens.")
    if ".." in value or "/" in value or "\\" in value:
        raise ValueError(f"{field_name} contains unsafe path characters.")
    return value


def _report_path(report_id: str, output_dir: str | Path = DEFAULT_BACKTEST_REPORT_DIR) -> Path:
    safe_report_id = _validate_safe_name(report_id, "report_id")
    base_dir = _ensure_report_dir(output_dir)
    path = (base_dir / f"{safe_report_id}.json").resolve()
    if base_dir != path.parent:
        raise ValueError("Report path must stay inside the backtest report directory.")
    return path


def _has_sensitive_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_").replace(" ", "_")
            if normalized in SENSITIVE_KEYS or normalized.endswith("_secret") or normalized.endswith("_token"):
                return True
            if _has_sensitive_key(item):
                return True
    elif isinstance(value, list):
        return any(_has_sensitive_key(item) for item in value)
    return False


def _json_safe(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        return value.item()
    if pd.isna(value):
        return None
    return value


def _dataframe_records(data: pd.DataFrame | None) -> list[dict]:
    if data is None:
        return []
    result = data.copy()
    for column in result.columns:
        if pd.api.types.is_datetime64_any_dtype(result[column]):
            result[column] = result[column].dt.strftime("%Y-%m-%dT%H:%M:%S")
    return [_json_safe(record) for record in result.to_dict(orient="records")]


def generate_report_id(prefix: str = "backtest") -> str:
    """Generate a path-safe report id with timestamp and random suffix."""
    safe_prefix = _validate_safe_name(prefix, "prefix")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = secrets.token_hex(4)
    return f"{safe_prefix}_{timestamp}_{suffix}"


def save_backtest_report(
    report_type: str,
    parameters: dict,
    summary: dict,
    equity_curve: pd.DataFrame | None = None,
    trades: pd.DataFrame | None = None,
    output_dir: str | Path = DEFAULT_BACKTEST_REPORT_DIR,
) -> dict:
    """Save one local backtest report as JSON."""
    if _has_sensitive_key(parameters) or _has_sensitive_key(summary):
        raise ValueError("Backtest reports must not contain API keys, secrets, passwords, or tokens.")

    report_id = generate_report_id("backtest")
    report = {
        "report_id": report_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "report_type": str(report_type),
        "parameters": _json_safe(parameters),
        "summary": _json_safe(summary),
        "equity_curve": _dataframe_records(equity_curve),
        "trades": _dataframe_records(trades),
    }
    if _has_sensitive_key(report):
        raise ValueError("Backtest reports must not contain API keys, secrets, passwords, or tokens.")

    path = _report_path(report_id, output_dir)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return report


def load_backtest_report(report_id: str, output_dir: str | Path = DEFAULT_BACKTEST_REPORT_DIR) -> dict:
    """Load one saved backtest report by id."""
    path = _report_path(report_id, output_dir)
    if not path.exists():
        raise FileNotFoundError(f"Backtest report not found: {report_id}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Backtest report JSON is invalid: {report_id}") from error


def list_backtest_reports(output_dir: str | Path = DEFAULT_BACKTEST_REPORT_DIR) -> pd.DataFrame:
    """List saved reports as a compact summary table."""
    base_dir = _ensure_report_dir(output_dir)
    rows = []
    for path in sorted(base_dir.glob("*.json"), reverse=True):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        summary = report.get("summary", {})
        rows.append(
            {
                "report_id": report.get("report_id", path.stem),
                "created_at": report.get("created_at"),
                "report_type": report.get("report_type"),
                "total_return": summary.get("total_return"),
                "annualized_return": summary.get("annualized_return"),
                "max_drawdown": summary.get("max_drawdown"),
                "number_of_trades": summary.get("number_of_trades"),
                "final_portfolio_value": summary.get("final_portfolio_value"),
            }
        )
    return pd.DataFrame(rows, columns=SUMMARY_COLUMNS)


def delete_backtest_report(report_id: str, output_dir: str | Path = DEFAULT_BACKTEST_REPORT_DIR) -> None:
    """Delete one saved report inside the report directory."""
    path = _report_path(report_id, output_dir)
    if not path.exists():
        raise FileNotFoundError(f"Backtest report not found: {report_id}")
    path.unlink()


def export_report_summary_csv(output_dir: str | Path = DEFAULT_BACKTEST_REPORT_DIR) -> str:
    """Export report summaries as a CSV string."""
    reports = list_backtest_reports(output_dir)
    return reports.to_csv(index=False)
