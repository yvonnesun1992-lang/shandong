from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime.security_scan import scan_sandbox_outputs
from sandbox.sandbox_readiness_report import generate_sandbox_readiness_report


def main() -> int:
    result = generate_sandbox_readiness_report()
    scan = scan_sandbox_outputs(result, report_path=result["path"])
    if not scan["safe"]:
        result["verdict"] = "FAIL"
        result.setdefault("summary", {})["errors"] = scan["findings"]
    print(json.dumps(result, indent=2, default=str))
    return 0 if result["verdict"] in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
