from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime.v55_deployment_report import generate_v55_deployment_report


def main() -> int:
    result = generate_v55_deployment_report()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("verdict") == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
