from __future__ import annotations

from pathlib import Path

from runtime.monitoring_summary import build_monitoring_summary


def generate_monitoring_report(path: str | Path = "reports/v5_4_monitoring_report.md") -> dict:
    summary = build_monitoring_summary()
    verdict = _verdict(summary)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# V5.4 Live Paper Trading Monitoring Report",
        "",
        "## Latest System Status",
        f"- Status: {summary['status']}",
        f"- Mode: {summary['mode']}",
        f"- Latest equity: {summary['latest_equity']}",
        f"- Cash: {summary['cash']}",
        f"- Position value: {summary['position_value']}",
        f"- Open positions count: {len(summary['open_positions'])}",
        "",
        "## Runtime Activity",
        f"- Recent signal count: {len(summary['recent_signals'])}",
        f"- Recent trade count: {len(summary['recent_trades'])}",
        f"- Recent error count: {len(summary['recent_errors'])}",
        "",
        "## Health Summary",
        f"- Health: {summary['health']}",
        "",
        "## Risk Summary",
        f"- Risk: {summary['risk']}",
        "",
        "## Soak Test Report",
        f"- Soak report status: {summary['soak_report'].get('status', 'UNKNOWN')}",
        "",
        "## Safety Boundary",
        "- Paper trading only",
        "- No real broker connected",
        "- No real orders",
        "- No real capital",
        "- No production deployment",
        "- No external log upload",
        "",
        "## Final Monitoring Verdict",
        verdict,
    ]
    output.write_text("\n".join(lines), encoding="utf-8")
    return {"path": output.as_posix(), "verdict": verdict, "summary": summary}


def _verdict(summary: dict) -> str:
    if summary["status"] == "FAILED":
        return "FAIL"
    if summary["status"] in {"DEGRADED", "UNKNOWN"} or summary["mode"] in {"SAFE_MODE", "UNKNOWN"} or summary["warnings"]:
        return "WARNING"
    return "PASS"
