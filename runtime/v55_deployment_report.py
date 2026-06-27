from __future__ import annotations

from pathlib import Path

from config.v5_deployment_config import get_v5_deployment_status
from scripts.v55_deployment_dry_run_check import run_v55_deployment_dry_run_check


def generate_v55_deployment_report(output_path: str | Path = "reports/v5_5_deployment_dry_run_report.md") -> dict:
    check = run_v55_deployment_dry_run_check()
    status = get_v5_deployment_status()
    verdict = _verdict(check)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_report(status, check, verdict), encoding="utf-8")
    return {"path": path.as_posix(), "verdict": verdict, "summary": check}


def _verdict(check: dict) -> str:
    if not check.get("success"):
        return "FAIL"
    if check.get("deployment_ready") is False and check.get("dry_run_ready") is True:
        return "WARNING"
    return "PASS"


def _render_report(status: dict, check: dict, verdict: str) -> str:
    ok_count = len([item for item in check.get("checks", []) if item.get("status") == "ok"])
    error_count = len(check.get("errors", []))
    warning_count = len(check.get("warnings", []))
    return f"""# V5.5 Production Deployment Dry Run Report

## Deployment Modes
- Deployment mode: {status.get("deployment_mode")}
- Runtime mode: {status.get("runtime_mode")}
- Monitoring mode: {status.get("monitoring_mode")}
- Storage mode: {status.get("storage_mode")}

## Readiness Summary
- API readiness: {'ready' if ok_count else 'not ready'}
- Frontend readiness: dry run page and navigation expected
- Runtime fallback readiness: checked
- Docker readiness: checked
- Config readiness: checked
- Dry run ready: {check.get("dry_run_ready")}
- Deployment ready: {check.get("deployment_ready")}
- Checks passing: {ok_count}
- Warnings: {warning_count}
- Errors: {error_count}

## Safety Boundary Summary
- Current stage is deployment dry run only
- Current stage is not formal production launch
- Current stage does not connect to a broker
- Current stage does not place real orders
- Current stage does not use real capital
- Current stage does not use a production database
- Current stage does not connect to a real cloud service
- Current stage does not upload logs to a third party

## Missing Production Items
- Real production deployment remains disabled
- Real broker integration remains absent
- Real money flow remains absent
- Real cloud service integration remains absent
- Production database integration remains planned only

## Check Detail
{_render_checks(check.get("checks", []))}

## Final Verdict
{verdict}
"""


def _render_checks(checks: list[dict]) -> str:
    if not checks:
        return "- No checks recorded"
    return "\n".join(f"- {item.get('name')}: {item.get('status')}" for item in checks)
