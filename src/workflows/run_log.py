from __future__ import annotations

import json
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_WORKFLOW_RUN_DIR = Path(__file__).resolve().parents[2] / "reports" / "workflow_runs"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
SENSITIVE_KEYS = {"api_key", "apikey", "secret", "password", "token"}
SUMMARY_COLUMNS = [
    "run_id",
    "created_at",
    "market",
    "watchlist_name",
    "success",
    "total_symbols",
    "success_count",
    "failed_count",
    "report_id",
    "elapsed_seconds",
]


def _ensure_run_dir(output_dir: str | Path = DEFAULT_WORKFLOW_RUN_DIR) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _validate_run_id(run_id: str) -> str:
    clean_run_id = str(run_id).strip()
    if not clean_run_id or not RUN_ID_PATTERN.fullmatch(clean_run_id):
        raise ValueError("run_id may only contain letters, numbers, underscores, and hyphens.")
    if ".." in clean_run_id or "/" in clean_run_id or "\\" in clean_run_id:
        raise ValueError("run_id contains unsafe path characters.")
    return clean_run_id


def _run_log_path(run_id: str, output_dir: str | Path = DEFAULT_WORKFLOW_RUN_DIR) -> Path:
    safe_run_id = _validate_run_id(run_id)
    base_dir = _ensure_run_dir(output_dir)
    path = (base_dir / f"{safe_run_id}.json").resolve()
    if path.parent != base_dir:
        raise ValueError("Workflow run log path must stay inside the workflow run directory.")
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
    if isinstance(value, pd.DataFrame):
        return [_json_safe(record) for record in value.to_dict(orient="records")]
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
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def generate_run_id(prefix: str = "workflow_run") -> str:
    safe_prefix = _validate_run_id(prefix)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = secrets.token_hex(4)
    return f"{safe_prefix}_{timestamp}_{suffix}"


def save_workflow_run_log(
    workflow_result: dict,
    output_dir: str | Path = DEFAULT_WORKFLOW_RUN_DIR,
) -> dict:
    clean_log = _json_safe(workflow_result)
    if _has_sensitive_key(clean_log):
        raise ValueError("Workflow run logs must not contain API keys, secrets, passwords, or tokens.")

    run_id = str(clean_log.get("run_id") or generate_run_id())
    clean_log["run_id"] = _validate_run_id(run_id)
    clean_log.setdefault("created_at", clean_log.get("finished_at") or datetime.now().isoformat(timespec="seconds"))

    path = _run_log_path(clean_log["run_id"], output_dir)
    path.write_text(json.dumps(clean_log, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return clean_log


def list_workflow_run_logs(
    output_dir: str | Path = DEFAULT_WORKFLOW_RUN_DIR,
) -> pd.DataFrame:
    base_dir = _ensure_run_dir(output_dir)
    rows = []
    for path in sorted(base_dir.glob("*.json"), reverse=True):
        try:
            log = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"Workflow run log JSON is invalid: {path.name}") from error
        rows.append(
            {
                "run_id": log.get("run_id", path.stem),
                "created_at": log.get("created_at") or log.get("finished_at") or log.get("started_at"),
                "market": log.get("market"),
                "watchlist_name": log.get("watchlist_name"),
                "success": log.get("success"),
                "total_symbols": log.get("total_symbols"),
                "success_count": log.get("success_count"),
                "failed_count": log.get("failed_count"),
                "report_id": log.get("report_id"),
                "elapsed_seconds": log.get("elapsed_seconds"),
            }
        )
    return pd.DataFrame(rows, columns=SUMMARY_COLUMNS)


def load_workflow_run_log(
    run_id: str,
    output_dir: str | Path = DEFAULT_WORKFLOW_RUN_DIR,
) -> dict:
    path = _run_log_path(run_id, output_dir)
    if not path.exists():
        raise FileNotFoundError(f"Workflow run log not found: {run_id}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Workflow run log JSON is invalid: {run_id}") from error


def delete_workflow_run_log(
    run_id: str,
    output_dir: str | Path = DEFAULT_WORKFLOW_RUN_DIR,
) -> None:
    path = _run_log_path(run_id, output_dir)
    if not path.exists():
        raise FileNotFoundError(f"Workflow run log not found: {run_id}")
    path.unlink()


def export_workflow_run_summary_csv(
    output_dir: str | Path = DEFAULT_WORKFLOW_RUN_DIR,
) -> str:
    logs = list_workflow_run_logs(output_dir)
    return logs.to_csv(index=False)
