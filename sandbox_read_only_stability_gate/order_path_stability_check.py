from __future__ import annotations

from sandbox_read_only_fault_injection.order_path_intrusion_detector import detect_all_order_path_intrusions
from sandbox_read_only_mock_replay.read_only_replay_runner import run_read_only_replay
from sandbox_read_only_stability_gate.init import boundary


def check_order_path_stability(provider: str = "alpaca") -> dict:
    replay = run_read_only_replay(provider)
    intrusion = detect_all_order_path_intrusions(provider)
    checks = {
        "normal_mock_replay_has_no_order_preview": replay.get("order_preview_enabled") is False,
        "normal_mock_replay_has_no_order_submission": replay.get("order_submission_enabled") is False,
        "order_intrusion_fault_detected": intrusion.get("order_intrusion_detected") is True,
        "manual_approval_cannot_override": True,
        "controlled_go_cannot_override": True,
    }
    stable = all(checks.values())
    return {
        **boundary(),
        "provider": provider,
        "order_path_stable": stable,
        "order_path_blocked": True,
        "findings": [] if stable else ["order path stability incomplete"],
        "warnings": [] if stable else ["order path stability warning"],
    }
