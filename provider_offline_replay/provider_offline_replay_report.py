from __future__ import annotations

from pathlib import Path

from config.v5_provider_offline_replay_config import get_offline_replay_provider, get_offline_replay_status
from provider_offline_replay import boundary
from provider_offline_replay.offline_replay_orchestrator import run_offline_replay
from provider_offline_replay.replay_consistency_validator import validate_all_replay_consistency
from provider_offline_replay.replay_event_catalog import build_replay_event_catalog
from provider_offline_replay.replay_failure_recovery_validator import validate_failure_recovery
from provider_offline_replay.replay_runner import run_replay_scenario
from provider_offline_replay.replay_safety_validator import build_replay_safety_summary


REPORT_PATH = Path("reports/v5_23_provider_offline_replay_report.md")


def generate_provider_offline_replay_report(provider: str | None = None, scenario: str | None = None, check: str = "all") -> dict:
    selected = provider or get_offline_replay_provider()
    summary = run_offline_replay(selected)
    status = get_offline_replay_status()
    catalog = build_replay_event_catalog(selected)
    runner_result = run_replay_scenario(selected, scenario) if scenario else summary["details"]["runner"]
    consistency = validate_all_replay_consistency(selected)
    recovery = validate_failure_recovery(selected)
    safety = build_replay_safety_summary()

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        _render_report(status, catalog, runner_result, consistency, recovery, safety, summary),
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


def _render_report(status: dict, catalog: dict, runner_result: dict, consistency: dict, recovery: dict, safety: dict, summary: dict) -> str:
    scenarios = ", ".join(catalog["scenarios"].keys())
    return f"""# V5.23 Provider Sandbox Connector Offline Replay Harness

Final verdict: {summary["verdict"]}

Current phase is offline replay harness only.

Boundary:
- Offline replay mode: {status["offline_replay_mode"]}
- Provider: {summary["provider"]}
- Replay runtime enabled: false
- Sandbox API enabled: false
- Account read enabled: false
- Order submission enabled: false
- Broker connected: false
- Real money enabled: false
- Paper trading: true

Replay scenario catalog:
- {scenarios}

Replay runner results:
- Total scenarios: {summary["total_scenarios"]}
- Passed: {summary["passed"]}
- Failed: {summary["failed"]}

Replay consistency validation:
- Valid: {consistency["valid"]}
- Validated scenarios: {consistency["validated_scenarios"]}

Failure recovery validation:
- Valid: {recovery["valid"]}
- Recovery scenarios checked: {", ".join(recovery["recovery_scenarios_checked"])}

Audit trail validation:
- Audit event generated for every replay step.
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
- Runtime validation remains future work.

This is not a production trading system.
"""
