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
    confidence_level: str = "Unknown"
    data_freshness_score: float = 0.0
    stability_index: float = 0.0
    schema_version: str = "StandardReportV1"

    @classmethod
    def from_existing_report(cls, report: dict) -> "StandardReportV1":
        module_summaries = report.get("module_summaries", {}) or {}
        quality_summary = report.get("quality_summary", {}) or module_summaries.get("quality", {}) or {}
        stability_summary = module_summaries.get("stability", {}) or {}
        return cls(
            strategy_name=str(report.get("strategy_name") or "Unnamed strategy"),
            generated_at=str(report.get("generated_at") or datetime.now(timezone.utc).isoformat()),
            backtest_summary=module_summaries.get("backtest", {}) or {},
            quality_summary=quality_summary,
            risk_summary=module_summaries.get("risk", {}) or {},
            stability_summary=stability_summary,
            out_of_sample_summary=module_summaries.get("out_of_sample", {}) or {},
            stress_summary=module_summaries.get("stress", {}) or {},
            confidence_level=str(report.get("confidence_level") or _confidence_from_quality(quality_summary)),
            data_freshness_score=float(report.get("data_freshness_score", quality_summary.get("data_quality_score", 0.0)) or 0.0),
            stability_index=float(report.get("stability_index", stability_summary.get("stable_window_ratio", 0.0)) or 0.0),
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
            "confidence_level": self.confidence_level,
            "data_freshness_score": float(self.data_freshness_score or 0.0),
            "stability_index": float(self.stability_index or 0.0),
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


def _confidence_from_quality(quality_summary: dict) -> str:
    score = float((quality_summary or {}).get("total_quality_score", 0.0) or 0.0)
    if score >= 75:
        return "High"
    if score >= 55:
        return "Medium"
    if score > 0:
        return "Low"
    return "Unknown"
