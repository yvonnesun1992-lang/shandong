from __future__ import annotations

from guided_setup.command_copy_blocks import build_command_copy_blocks
from guided_setup.guided_setup_safety_validator import validate_guided_setup_safety
from guided_setup.init import boundary
from guided_setup.plain_language_explanation import build_plain_language_summary
from guided_setup.setup_requirement_detector import detect_setup_requirements
from guided_setup.setup_step_model import build_mac_setup_steps, build_windows_setup_steps, mark_setup_steps_status


def build_guided_setup_wizard() -> dict:
    requirements = detect_setup_requirements()
    steps = mark_setup_steps_status(requirements)
    commands = build_command_copy_blocks()
    explanation = build_plain_language_summary(requirements)
    payload = {
        "guided_setup_ready": requirements["setup_ready"],
        "likely_blocker": requirements["likely_blocker"],
        "missing_requirements": requirements["missing_requirements"],
        "mac_steps": build_mac_setup_steps(),
        "windows_steps": build_windows_setup_steps(),
        "steps": steps["steps"],
        "command_blocks": commands["command_blocks"],
        "plain_language_summary": explanation["plain_language_summary"],
        "recommended_next_step": explanation["recommended_next_step"],
        "requirements": requirements,
        "commands": commands,
        "warnings": [] if requirements["setup_ready"] else [requirements["likely_blocker"]],
        "errors": [],
        **boundary(),
    }
    safety = validate_guided_setup_safety(payload)
    payload["safety_validation"] = safety
    if payload["errors"] or not safety["safe"]:
        payload["verdict"] = "FAIL"
    elif payload["warnings"] or not payload["guided_setup_ready"]:
        payload["verdict"] = "WARNING"
    else:
        payload["verdict"] = "PASS"
    return payload


def summarize_guided_setup_wizard(result: dict) -> dict:
    return {
        "guided_setup_ready": result.get("guided_setup_ready", False),
        "likely_blocker": result.get("likely_blocker", ""),
        "missing_requirements": result.get("missing_requirements", []),
        "recommended_next_step": result.get("recommended_next_step", ""),
        "warnings": result.get("warnings", []),
        "errors": result.get("errors", []),
        "verdict": result.get("verdict", "FAIL"),
        **boundary(),
    }
