from __future__ import annotations

from sandbox_read_only_mock_replay.mock_read_only_payloads import build_mock_read_only_payload
from sandbox_read_only_mock_replay.read_only_audit_replay import build_read_only_mock_audit_trail
from sandbox_read_only_mock_replay.read_only_mock_replay_orchestrator import run_read_only_mock_replay, summarize_read_only_mock_replay
from sandbox_read_only_stability_gate.init import boundary


def collect_replay_evidence(provider: str = "alpaca") -> dict:
    account = build_mock_read_only_payload(provider, "account_snapshot_placeholder")
    balance = build_mock_read_only_payload(provider, "balance_snapshot_placeholder")
    position = build_mock_read_only_payload(provider, "position_snapshot_placeholder")
    summary = summarize_read_only_mock_replay(run_read_only_mock_replay(provider))
    audit = build_read_only_mock_audit_trail(provider)
    checks = {
        "mock_payload_catalog_exists": summary.get("payload_count", 0) > 0,
        "account_payload_placeholder_only": account.get("account_ref") == "ACCOUNT_REF_PLACEHOLDER",
        "balance_payload_redacted_only": balance.get("cash_balance") == "REDACTED_PLACEHOLDER",
        "position_payload_redacted_only": position.get("quantity") == "REDACTED_PLACEHOLDER",
        "schema_validation_passed": summary.get("safe") is True,
        "redaction_validation_passed": summary.get("safe") is True,
        "audit_replay_generated": bool(audit.get("audit_events")),
        "order_path_remained_inactive": summary.get("order_submission_enabled") is False,
        "sandbox_api_disabled": summary.get("sandbox_api_enabled") is False,
        "secret_read_disabled": summary.get("secret_read_enabled") is False,
        "account_read_disabled": summary.get("account_read_enabled") is False,
        "balance_read_disabled": summary.get("balance_read_enabled") is False,
        "position_read_disabled": summary.get("position_read_enabled") is False,
        "order_submission_disabled": summary.get("order_submission_enabled") is False,
    }
    ready = all(checks.values())
    return {
        **boundary(),
        "provider": provider,
        "replay_evidence_ready": ready,
        "mock_replay_passed": ready,
        "evidence_items": checks,
        "warnings": [] if ready else ["mock replay evidence incomplete"],
    }


def summarize_replay_evidence(evidence: dict) -> dict:
    return {
        **boundary(),
        "provider": evidence.get("provider", "alpaca"),
        "replay_evidence_ready": evidence.get("replay_evidence_ready", False),
        "mock_replay_passed": evidence.get("mock_replay_passed", False),
        "warnings": evidence.get("warnings", []),
    }
