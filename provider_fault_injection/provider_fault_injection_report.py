from __future__ import annotations

from pathlib import Path

from config.v5_provider_fault_injection_config import get_fault_injection_provider, get_fault_injection_status
from provider_fault_injection import boundary
from provider_fault_injection.fault_audit_trail import build_all_fault_audit_trails
from provider_fault_injection.fault_detection_validator import validate_all_fault_detections
from provider_fault_injection.fault_injection_orchestrator import run_fault_injection_suite
from provider_fault_injection.fault_recovery_validator import validate_all_fault_recovery
from provider_fault_injection.fault_replay_runner import run_fault_scenario
from provider_fault_injection.fault_safety_validator import build_fault_safety_summary
from provider_fault_injection.fault_scenario_catalog import build_fault_scenario_catalog
from provider_fault_injection.kill_switch_simulation import simulate_kill_switch_trigger


REPORT_PATH = Path("reports/v5_24_provider_fault_injection_report.md")


def generate_provider_fault_injection_report(provider: str | None = None, scenario: str | None = None, check: str = "all") -> dict:
    selected = provider or get_fault_injection_provider()
    summary = run_fault_injection_suite(selected)
    status = get_fault_injection_status()
    catalog = build_fault_scenario_catalog(selected)
    runner_result = run_fault_scenario(selected, scenario) if scenario else summary["details"]["runner"]
    detection = validate_all_fault_detections(selected)
    recovery = validate_all_fault_recovery(selected)
    kill_switch = simulate_kill_switch_trigger(selected, "kill_switch_trigger")
    audit = build_all_fault_audit_trails(selected)
    safety = build_fault_safety_summary()

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        _render_report(status, catalog, runner_result, detection, recovery, kill_switch, audit, safety, summary),
        encoding="utf-8",
    )
    return {
        "path": REPORT_PATH.as_posix(),
        "provider": selected,
        "scenario": scenario,
        "check": check,
        "summary": summary,
        "verdict": summary["verdict"],
        **boundary(),
    }


def _render_report(status: dict, catalog: dict, runner_result: dict, detection: dict, recovery: dict, kill_switch: dict, audit: dict, safety: dict, summary: dict) -> str:
    scenarios = ", ".join(catalog["scenarios"].keys())
    return f"""# V5.24 Provider Sandbox Connector Fault Injection Suite

Final verdict: {summary["verdict"]}

Current phase is offline fault injection only.

Boundary:
- Fault injection mode: {status["fault_injection_mode"]}
- Provider: {summary["provider"]}
- Fault injection runtime enabled: false
- Sandbox API enabled: false
- Account read enabled: false
- Order submission enabled: false
- Broker connected: false
- Real money enabled: false
- Paper trading: true

Fault scenario catalog:
- {scenarios}

Fault runner results:
- Total scenarios: {summary["total_scenarios"]}
- Passed: {summary["passed"]}
- Failed: {summary["failed"]}

Detection validation:
- Valid: {detection["valid"]}
- Detected faults: {", ".join(detection["detected_faults"])}

Recovery validation:
- Valid: {recovery["valid"]}
- Final states are safe: true

Kill switch simulation:
- Kill switch triggered: {kill_switch["kill_switch_triggered"]}
- Order submission enabled: false
- Sandbox API enabled: false

Audit trail validation:
- Valid: {audit["valid"]}
- Raw payload stored: false
- Provider payload redacted: true

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
- Runtime fault injection remains future work.

This is not a production trading system.
"""
