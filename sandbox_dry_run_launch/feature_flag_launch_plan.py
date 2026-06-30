from __future__ import annotations

from sandbox_dry_run_launch.init import boundary


DEFAULT_FLAGS = {
    "ENABLE_DRY_RUN_RUNTIME": False,
    "ENABLE_SANDBOX_API": False,
    "ENABLE_SECRET_READ": False,
    "ENABLE_ACCOUNT_READ": False,
    "ENABLE_ORDER_PREVIEW": False,
    "ENABLE_ORDER_SUBMISSION": False,
    "ENABLE_REAL_MONEY": False,
    "REQUIRE_OPERATOR_APPROVAL": True,
    "REQUIRE_KILL_SWITCH": True,
    "REQUIRE_ROLLBACK_PLAN": True,
    "REQUIRE_AUDIT_LOGGING": True,
}


def build_feature_flag_launch_plan(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "flags": dict(DEFAULT_FLAGS),
        "validation": validate_feature_flag_plan(DEFAULT_FLAGS),
    }


def validate_feature_flag_plan(flags: dict) -> dict:
    invalid = []
    for key in ["ENABLE_ORDER_SUBMISSION", "ENABLE_REAL_MONEY", "ENABLE_SANDBOX_API", "ENABLE_SECRET_READ", "ENABLE_ACCOUNT_READ"]:
        if flags.get(key) is True:
            invalid.append(f"{key} must remain false in V5.29")
    return {
        **boundary(),
        "valid": not invalid,
        "invalid_items": invalid,
        "warnings": [] if not invalid else ["feature flags requested real path access and were rejected"],
    }
