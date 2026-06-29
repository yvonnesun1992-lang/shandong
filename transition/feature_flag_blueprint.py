from __future__ import annotations


def build_feature_flag_blueprint() -> dict:
    flags = {
        "ENABLE_SANDBOX_CONNECTOR": False,
        "ENABLE_SANDBOX_ORDER_SUBMISSION": False,
        "ENABLE_REAL_BROKER_CONNECTOR": False,
        "ENABLE_REAL_ORDER_SUBMISSION": False,
        "ENABLE_REAL_MONEY": False,
        "REQUIRE_MANUAL_APPROVAL": True,
        "ENABLE_KILL_SWITCH": True,
        "ENABLE_AUDIT_LOGGING": True,
    }
    return {
        "version": "V5.18",
        "blueprint_only": True,
        "flags": flags,
        "validation": validate_feature_flags(flags),
        "transition_enabled": False,
        "sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }


def validate_feature_flags(flags: dict) -> dict:
    errors = []
    if flags.get("ENABLE_REAL_ORDER_SUBMISSION") and not flags.get("REQUIRE_MANUAL_APPROVAL"):
        errors.append("real order flag requires manual approval")
    if flags.get("ENABLE_REAL_MONEY"):
        errors.append("real money flag is invalid in V5.18")
    return {"valid": not errors, "errors": errors}
