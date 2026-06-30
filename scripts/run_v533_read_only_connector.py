from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_read_only_connector_config import get_read_only_connector_provider, get_read_only_connector_status
from sandbox_read_only_connector.read_only_connector_orchestrator import (
    build_read_only_connector_blueprint,
    summarize_read_only_connector_blueprint,
)
from sandbox_read_only_connector.read_only_redaction_policy import build_redaction_policy
from sandbox_read_only_connector.read_only_safety_validator import build_read_only_safety_summary
from sandbox_read_only_connector.read_only_scope_definition import build_read_only_scope_definition
from sandbox_read_only_connector.sandbox_read_only_connector_report import generate_sandbox_read_only_connector_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.33 read-only connector blueprint checks.")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--check", choices=["all", "scope", "redaction", "safety"], default="all")
    args = parser.parse_args()
    provider = args.provider or get_read_only_connector_provider()

    if args.check == "scope":
        payload = {**build_read_only_scope_definition(provider), "verdict": "WARNING"}
    elif args.check == "redaction":
        payload = {**build_redaction_policy(provider), "verdict": "WARNING"}
    elif args.check == "safety":
        payload = {**build_read_only_safety_summary(), "provider": provider, "verdict": "WARNING"}
    else:
        report = generate_sandbox_read_only_connector_report(provider=provider, check=args.check)
        payload = {
            **report,
            "status": get_read_only_connector_status(),
            "summary": summarize_read_only_connector_blueprint(build_read_only_connector_blueprint(provider)),
        }

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("verdict") in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    sys.exit(main())
