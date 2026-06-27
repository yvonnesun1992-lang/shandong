from __future__ import annotations

from pathlib import Path


def final_verdict(summary: dict, consistency: dict, security: dict) -> str:
    if summary.get("errors") or not consistency.get("consistent") or not security.get("safe"):
        return "FAIL"
    if summary.get("health_status") == "FAILED" or summary.get("risk_kill_switch_triggered"):
        return "WARNING"
    if summary.get("error_count", 0) > 0 or summary.get("health_status") == "DEGRADED":
        return "WARNING"
    return "PASS"


def format_soak_report(summary: dict, consistency: dict, security: dict) -> str:
    lines = [
        "# V5.3 Long-Run Paper Trading Soak Test Report",
        "",
        "## Test Configuration",
        f"- Mode: {summary.get('run_mode', summary.get('mode'))}",
        f"- Market regime: {summary.get('market_regime')}",
        f"- Symbols: {', '.join(summary.get('symbols', []))}",
        f"- Fault injection: {summary.get('fault_injection')}",
        "",
        "## Runtime Summary",
        f"- Duration seconds: {summary.get('duration_seconds')}",
        f"- Ticks processed: {summary.get('ticks_processed')}",
        f"- Final equity: {summary.get('final_equity')}",
        f"- Max drawdown: {summary.get('max_drawdown')}",
        f"- Error count: {summary.get('error_count')}",
        f"- Restart count: {summary.get('restart_count')}",
        f"- Checkpoint count: {summary.get('checkpoint_count')}",
        "",
        "## Health Status Timeline",
        f"- Final health status: {summary.get('health_status')}",
        "",
        "## Mode Transition Summary",
        f"- Final mode: {summary.get('mode_state')}",
        "",
        "## Risk Trigger Summary",
        f"- Risk kill switch triggered: {summary.get('risk_kill_switch_triggered')}",
        "",
        "## Consistency Validation",
        f"- Consistent: {consistency.get('consistent')}",
        f"- Checks: {', '.join(consistency.get('checks', []))}",
        f"- Errors: {consistency.get('errors', [])}",
        "",
        "## Sensitive Data Scan",
        f"- Safe: {security.get('safe')}",
        f"- Findings: {security.get('findings', [])}",
        "",
        "## Final verdict",
        summary.get("final_verdict", "FAIL"),
        "",
        "## Safety",
        "- Paper trading only",
        "- No broker connection",
        "- No real trading",
        "- No real account",
        "- No payment system",
    ]
    return "\n".join(lines)


def save_soak_report(summary: dict, consistency: dict, security: dict, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(format_soak_report(summary, consistency, security), encoding="utf-8")
    return output
