from __future__ import annotations

from pathlib import Path

from config.v5_provider_offline_soak_config import get_offline_soak_provider, get_offline_soak_status
from provider_offline_soak import boundary
from provider_offline_soak.offline_soak_orchestrator import run_offline_soak, summarize_offline_soak_results
from provider_offline_soak.soak_coverage_validator import validate_soak_coverage
from provider_offline_soak.soak_runner import run_soak_scenario
from provider_offline_soak.soak_safety_validator import build_soak_safety_summary
from provider_offline_soak.soak_scenario_plan import build_soak_scenario_plan
from provider_offline_soak.stability_gate import evaluate_all_stability_gates
from provider_offline_soak.stability_metrics import compute_all_stability_metrics


REPORT_PATH = Path("reports/v5_25_provider_offline_soak_report.md")


def generate_provider_offline_soak_report(provider: str | None = None, scenario: str | None = None, check: str = "all") -> dict:
    selected = provider or get_offline_soak_provider()
    orchestration = run_offline_soak(selected)
    summary = summarize_offline_soak_results(orchestration)
    status = get_offline_soak_status()
    plan = build_soak_scenario_plan(selected)
    runner = run_soak_scenario(selected, scenario) if scenario else orchestration["runner"]
    metrics = compute_all_stability_metrics(selected)
    gates = evaluate_all_stability_gates(selected)
    coverage = validate_soak_coverage(selected)
    safety = build_soak_safety_summary()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(status, plan, runner, metrics, gates, coverage, safety, summary), encoding="utf-8")
    return {"path": REPORT_PATH.as_posix(), "provider": selected, "scenario": scenario, "check": check, "summary": summary, "verdict": summary["verdict"], **boundary()}


def _render_report(status: dict, plan: dict, runner: dict, metrics: dict, gates: dict, coverage: dict, safety: dict, summary: dict) -> str:
    scenarios = ", ".join(plan["scenarios"].keys())
    return f"""# V5.25 Provider Sandbox Offline Soak & Stability Gate

Final verdict: {summary["verdict"]}

Current phase is offline soak only.

Boundary:
- Offline soak mode: {status["offline_soak_mode"]}
- Provider: {summary["provider"]}
- Soak runtime enabled: false
- Sandbox API enabled: false
- Account read enabled: false
- Order submission enabled: false
- Broker connected: false
- Real money enabled: false
- Paper trading: true

Soak scenario plan:
- Scenarios: {scenarios}

Soak runner results:
- Total scenarios: {summary["total_scenarios"]}
- Passed: {summary["passed"]}
- Failed: {summary["failed"]}

Stability metrics:
- Average stability score: {metrics["average_stability_score"]}

Stability gate:
- Failed gates: {gates["failed"]}

Coverage validation:
- Coverage passed: {coverage["coverage_passed"]}

Safety validation:
- Safe: {safety["safe"]}
- No broker SDK import.
- No network calls.
- No plaintext credentials.
- No real account reference.
- No real order reference.
- No raw provider payload.
- No provider endpoint URL.

Missing production requirements:
- Real sandbox connector remains disabled.
- Sandbox API remains disabled.
- Account read remains disabled.
- Order submission remains disabled.
- Provider portal access remains disabled.
- Runtime soak remains future work.

This is not a production trading system.
"""
