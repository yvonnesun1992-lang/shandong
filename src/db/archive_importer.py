from __future__ import annotations

import json
from pathlib import Path

from src.config.database_config import DATABASE_URL
from src.db.repository import StrategyReportRepository, safe_identifier


DEFAULT_ARCHIVE_DIR = Path("reports/strategy_research_reports")


def import_archived_reports_to_db(
    user_id: str = "default",
    archive_dir: str | Path = DEFAULT_ARCHIVE_DIR,
    database_url: str | None = None,
) -> dict:
    imported_count = 0
    skipped_count = 0
    warnings: list[str] = []
    archive_path = Path(archive_dir)

    if not archive_path.exists():
        return {"imported_count": 0, "skipped_count": 0, "warnings": []}
    if not archive_path.is_dir():
        return {"imported_count": 0, "skipped_count": 1, "warnings": [f"archive path is not a directory: {archive_path}"]}

    repository = StrategyReportRepository(database_url or DATABASE_URL)
    for path in sorted(archive_path.glob("*.json")):
        if path.parent.resolve() != archive_path.resolve():
            skipped_count += 1
            warnings.append(f"skipped unsafe archive path: {path.name}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            skipped_count += 1
            warnings.append(f"failed to import {path.name}: {exc}")
            continue
        if not isinstance(payload, dict):
            skipped_count += 1
            warnings.append(f"failed to import {path.name}: archive payload is not an object")
            continue

        report_id = safe_identifier(str(payload.get("report_id") or path.stem), fallback=path.stem)
        try:
            repository.save_report(
                user_id=user_id,
                report_id=report_id,
                strategy_name=str(payload.get("strategy_name") or payload.get("strategy") or "legacy_strategy"),
                research_view=str(payload.get("research_view") or payload.get("view") or ""),
                quality_score=payload.get("quality_score"),
                quality_level=str(payload.get("quality_level") or ""),
                generated_at=payload.get("generated_at"),
                saved_at=payload.get("saved_at"),
                report_json=payload,
                markdown=str(payload.get("markdown") or payload.get("report_markdown") or ""),
            )
            imported_count += 1
        except Exception as exc:
            skipped_count += 1
            warnings.append(f"failed to save {path.name}: {exc}")

    return {"imported_count": imported_count, "skipped_count": skipped_count, "warnings": warnings}
