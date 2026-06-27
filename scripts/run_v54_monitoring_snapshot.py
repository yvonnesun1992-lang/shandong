from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.monitoring_report import generate_monitoring_report


def main() -> int:
    result = generate_monitoring_report()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
