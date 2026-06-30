from __future__ import annotations

from sandbox_controlled_enablement.init import boundary


STAGES = [
    "stage_0_plan_only",
    "stage_1_vault_reference_validation",
    "stage_2_secret_read_dry_check",
    "stage_3_sandbox_api_connectivity_check",
    "stage_4_read_only_account_check",
    "stage_5_order_preview_only",
    "stage_6_manual_approval_simulation",
    "stage_7_sandbox_order_submission_review_only",
    "stage_8_sandbox_order_submission_future_blocked",
]


def build_staged_unlock_plan(provider: str = "alpaca") -> dict:
    stages = []
    for stage in STAGES:
        stages.append(
            {
                "stage": stage,
                "enabled": False,
                "executable_now": False,
                "requires_future_approval": True,
                "blocked": stage == "stage_8_sandbox_order_submission_future_blocked",
                "allowed_actions": [],
            }
        )
    return {
        **boundary(),
        "provider": provider,
        "stages": stages,
        "current_stage": "stage_0_plan_only",
        "warnings": ["all V5.32 staged unlock paths are non-executable blueprint entries"],
    }
