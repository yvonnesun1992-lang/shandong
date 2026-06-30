from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_credential_vault_design_config import get_vault_design_provider
from credential_vault_design.credential_vault_design_report import generate_credential_vault_design_report
from credential_vault_design.secret_access_policy import build_secret_access_policy
from credential_vault_design.vault_safety_validator import build_vault_safety_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V5.27 credential vault design summary.")
    parser.add_argument("--provider", default=get_vault_design_provider())
    parser.add_argument("--check", default="all", choices=["all", "safety", "access-policy"])
    args = parser.parse_args()
    if args.check == "safety":
        check_result = build_vault_safety_summary()
    elif args.check == "access-policy":
        check_result = build_secret_access_policy()
    else:
        check_result = None
    report = generate_credential_vault_design_report(provider=args.provider, check=args.check)
    if check_result is not None:
        report["check_result"] = check_result
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
