from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.v5_guided_setup_config import get_guided_setup_status
from guided_setup.command_copy_blocks import build_command_copy_blocks
from guided_setup.guided_setup_orchestrator import build_guided_setup_wizard, summarize_guided_setup_wizard
from guided_setup.guided_setup_report import generate_guided_setup_report
from guided_setup.guided_setup_safety_validator import build_guided_setup_safety_summary
from guided_setup.plain_language_explanation import build_plain_language_summary
from guided_setup.setup_requirement_detector import detect_setup_requirements
from guided_setup.setup_step_model import mark_setup_steps_status


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.43 guided local setup wizard.")
    parser.add_argument("--check", choices=["status", "requirements", "steps", "commands", "explain", "safety", "report"])
    args = parser.parse_args()
    if args.check == "status":
        payload = get_guided_setup_status()
    elif args.check == "requirements":
        payload = detect_setup_requirements()
    elif args.check == "steps":
        payload = mark_setup_steps_status(detect_setup_requirements())
    elif args.check == "commands":
        payload = build_command_copy_blocks()
    elif args.check == "explain":
        payload = build_plain_language_summary(detect_setup_requirements())
    elif args.check == "safety":
        payload = build_guided_setup_safety_summary()
    elif args.check == "report":
        payload = generate_guided_setup_report()
    else:
        payload = summarize_guided_setup_wizard(build_guided_setup_wizard())
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if payload.get("verdict") == "FAIL" or payload.get("safe") is False else 0


if __name__ == "__main__":
    raise SystemExit(main())
