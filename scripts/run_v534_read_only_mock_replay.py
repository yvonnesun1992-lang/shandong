from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_read_only_mock_replay_config import get_read_only_mock_replay_provider, get_read_only_mock_replay_status
from sandbox_read_only_mock_replay.read_only_mock_replay_orchestrator import run_read_only_mock_replay, summarize_read_only_mock_replay
from sandbox_read_only_mock_replay.read_only_mock_replay_safety_validator import build_read_only_mock_replay_safety_summary
from sandbox_read_only_mock_replay.read_only_schema_validator import validate_all_read_only_schemas
from sandbox_read_only_mock_replay.redaction_replay_validator import validate_all_payload_redaction
from sandbox_read_only_mock_replay.sandbox_read_only_mock_replay_report import generate_sandbox_read_only_mock_replay_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.34 read-only mock replay checks.")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--check", choices=["all", "schema", "redaction", "safety"], default="all")
    args = parser.parse_args()
    provider = args.provider or get_read_only_mock_replay_provider()

    if args.check == "schema":
        payload = {**validate_all_read_only_schemas(provider), "verdict": "PASS"}
    elif args.check == "redaction":
        payload = {**validate_all_payload_redaction(provider), "verdict": "PASS"}
    elif args.check == "safety":
        payload = {**build_read_only_mock_replay_safety_summary(), "provider": provider, "verdict": "WARNING"}
    else:
        report = generate_sandbox_read_only_mock_replay_report(provider=provider, check=args.check)
        payload = {
            **report,
            "status": get_read_only_mock_replay_status(),
            "summary": summarize_read_only_mock_replay(run_read_only_mock_replay(provider)),
        }

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("verdict") in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    sys.exit(main())
