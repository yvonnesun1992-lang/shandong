from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


REQUIRED_STANDARD_REPORT_FIELDS = [
    "strategy_name",
    "generated_at",
    "backtest_summary",
    "quality_summary",
    "risk_summary",
]


@dataclass
class StandardReportV1:
    strategy_name: str
    generated_at: str
    backtest_summary: dict
    quality_summary: dict
    risk_summary: dict
    stability_summary: dict | None = field(default_factory=dict)
    out_of_sample_summary: dict | None = field(default_factory=dict)
    stress_summary: dict | None = field(default_factory=dict)
    schema_version: str = "StandardReportV1"

    @classmethod
    def from_existing_report(cls, report: dict) -> "StandardReportV1":
        module_summaries = report.get("module_summaries", {}) or {}
        return cls(
            strategy_name=str(report.get("strategy_name") or "Unnamed strategy"),
            generated_at=str(report.get("generated_at") or datetime.now(timezone.utc).isoformat()),
            backtest_summary=module_summaries.get("backtest", {}) or {},
            quality_summary=report.get("quality_summary", {}) or module_summaries.get("quality", {}) or {},
            risk_summary=module_summaries.get("risk", {}) or {},
            stability_summary=module_summaries.get("stability", {}) or {},
            out_of_sample_summary=module_summaries.get("out_of_sample", {}) or {},
            stress_summary=module_summaries.get("stress", {}) or {},
        )

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "strategy_name": self.strategy_name,
            "generated_at": self.generated_at,
            "backtest_summary": self.backtest_summary or {},
            "quality_summary": self.quality_summary or {},
            "risk_summary": self.risk_summary or {},
            "stability_summary": self.stability_summary or {},
            "out_of_sample_summary": self.out_of_sample_summary or {},
            "stress_summary": self.stress_summary or {},
        }


def validate_standard_report(report: dict) -> dict:
    missing_fields = [field_name for field_name in REQUIRED_STANDARD_REPORT_FIELDS if field_name not in (report or {})]
    type_errors = []
    for field_name in ["backtest_summary", "quality_summary", "risk_summary"]:
        if field_name in (report or {}) and not isinstance(report.get(field_name), dict):
            type_errors.append(field_name)
    return {
        "valid": not missing_fields and not type_errors,
        "missing_fields": missing_fields,
        "type_errors": type_errors,
    }
