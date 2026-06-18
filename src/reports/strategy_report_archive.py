from __future__ import annotations

import csv
import io
import json
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STRATEGY_REPORT_ARCHIVE_DIR = PROJECT_ROOT / "reports" / "strategy_research_reports"
REPORT_ID_PATTERN = re.compile(r"^strategy_report_[0-9]{8}_[0-9]{6}_[a-f0-9]{6}$")
SENSITIVE_KEYS = {"api_key", "apikey", "secret", "password", "token"}
SUMMARY_COLUMNS = [
    "report_id",
    "saved_at",
    "generated_at",
    "strategy_name",
    "research_view",
    "quality_score",
    "quality_level",
    "symbol_count",
]


def _archive_dir(output_dir: str | Path | None = None) -> Path:
    base_dir = Path(output_dir) if output_dir is not None else DEFAULT_STRATEGY_REPORT_ARCHIVE_DIR
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir.resolve()


def _validate_report_id(report_id: str) -> str:
    clean_id = str(report_id or "").strip()
    if not REPORT_ID_PATTERN.fullmatch(clean_id):
        raise ValueError("report_id is invalid or unsafe.")
    if ".." in clean_id or "/" in clean_id or "\\" in clean_id:
        raise ValueError("report_id contains unsafe path characters.")
    return clean_id


def _safe_path(report_id: str, suffix: str, output_dir: str | Path | None = None) -> Path:
    safe_id = _validate_report_id(report_id)
    base_dir = _archive_dir(output_dir)
    path = (base_dir / f"{safe_id}{suffix}").resolve()
    if path.parent != base_dir:
        raise ValueError("Strategy report archive path must stay inside the archive directory.")
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
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        return value.item()
    return value


def _generate_report_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = secrets.token_hex(3)
    return f"strategy_report_{timestamp}_{suffix}"


def _summary_from_report(report: dict, json_path: Path | None = None, markdown_path: Path | None = None) -> dict:
    quality = report.get("quality_summary", {}) or {}
    key_metrics = report.get("key_metrics", {}) or {}
    symbols = report.get("symbols", []) or []
    return {
        "report_id": report.get("report_id") or (json_path.stem if json_path else ""),
        "saved_at": report.get("saved_at"),
        "generated_at": report.get("generated_at"),
        "strategy_name": report.get("strategy_name"),
        "research_view": report.get("research_view"),
        "quality_score": quality.get("total_quality_score", key_metrics.get("quality_score")),
        "quality_level": quality.get("quality_level", key_metrics.get("quality_level")),
        "symbol_count": len(symbols),
        "json_path": str(json_path) if json_path else "",
        "markdown_path": str(markdown_path) if markdown_path and markdown_path.exists() else "",
    }


def save_strategy_research_report(
    report: dict,
    markdown: str | None = None,
    output_dir: str | Path | None = None,
) -> dict:
    """Save a strategy research report JSON and optional Markdown inside the archive directory."""
    clean_report = _json_safe(report or {})
    if _has_sensitive_key(clean_report):
        raise ValueError("Strategy research reports must not contain API keys, secrets, passwords, or tokens.")
    report_id = _generate_report_id()
    saved_at = datetime.now().isoformat(timespec="seconds")
    clean_report["report_id"] = report_id
    clean_report["saved_at"] = saved_at
    if _has_sensitive_key(clean_report):
        raise ValueError("Strategy research reports must not contain API keys, secrets, passwords, or tokens.")

    json_path = _safe_path(report_id, ".json", output_dir)
    json_path.write_text(json.dumps(clean_report, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

    markdown_path = None
    if markdown:
        markdown_path = _safe_path(report_id, ".md", output_dir)
        markdown_path.write_text(str(markdown), encoding="utf-8", newline="\n")

    summary = _summary_from_report(clean_report, json_path, markdown_path)
    return {
        "report_id": report_id,
        "json_path": str(json_path),
        "markdown_path": str(markdown_path) if markdown_path else "",
        "saved_at": saved_at,
        "strategy_name": summary["strategy_name"],
        "research_view": summary["research_view"],
        "quality_score": summary["quality_score"],
        "quality_level": summary["quality_level"],
    }


def list_strategy_research_reports(output_dir: str | Path | None = None) -> list[dict]:
    """List archived strategy research report summaries in reverse saved/generated time order."""
    base_dir = _archive_dir(output_dir)
    rows = []
    for path in base_dir.glob("*.json"):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        report_id = str(report.get("report_id") or path.stem)
        try:
            _validate_report_id(report_id)
        except ValueError:
            continue
        markdown_path = _safe_path(report_id, ".md", output_dir)
        rows.append(_summary_from_report(report, path.resolve(), markdown_path))
    return sorted(rows, key=lambda row: row.get("saved_at") or row.get("generated_at") or "", reverse=True)


def load_strategy_research_report(report_id: str, output_dir: str | Path | None = None) -> dict:
    """Load one archived strategy research report by safe report id."""
    path = _safe_path(report_id, ".json", output_dir)
    if not path.exists():
        raise FileNotFoundError(f"Strategy research report not found: {report_id}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Strategy research report JSON is invalid: {report_id}") from error


def delete_strategy_research_report(report_id: str, output_dir: str | Path | None = None) -> dict:
    """Delete archived JSON and Markdown files for one safe report id."""
    json_path = _safe_path(report_id, ".json", output_dir)
    markdown_path = _safe_path(report_id, ".md", output_dir)
    if not json_path.exists() and not markdown_path.exists():
        raise FileNotFoundError(f"Strategy research report not found: {report_id}")
    deleted = []
    for path in (json_path, markdown_path):
        if path.exists():
            path.unlink()
            deleted.append(str(path))
    return {"report_id": _validate_report_id(report_id), "deleted_paths": deleted, "deleted_count": len(deleted)}


def export_strategy_report_summary_csv(reports: list[dict]) -> bytes:
    """Export archived report summaries as UTF-8 CSV bytes."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=SUMMARY_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for row in reports or []:
        writer.writerow({column: row.get(column, "") for column in SUMMARY_COLUMNS})
    return output.getvalue().encode("utf-8-sig")
