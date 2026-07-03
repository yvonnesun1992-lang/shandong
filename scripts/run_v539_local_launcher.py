from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.v5_local_launcher_config import get_local_launcher_status
from local_launcher.backend_launcher import check_backend_health_placeholder, launch_backend
from local_launcher.browser_opener import open_browser
from local_launcher.environment_checker import run_environment_check
from local_launcher.frontend_launcher import check_frontend_health_placeholder, launch_frontend
from local_launcher.init import boundary
from local_launcher.launcher_log_manager import read_recent_launcher_logs
from local_launcher.local_launcher_orchestrator import run_local_launcher, summarize_local_launcher_result
from local_launcher.local_launcher_safety_validator import build_local_launcher_safety_summary
from local_launcher.port_checker import check_launcher_ports


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the V5.39 local desktop launcher.")
    parser.add_argument("--check", choices=["environment", "ports", "backend", "frontend", "browser", "safety", "logs", "status"])
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--run", action="store_true", default=False)
    args = parser.parse_args()

    dry_run = not args.run
    if args.check == "environment":
        payload = run_environment_check()
    elif args.check == "ports":
        payload = check_launcher_ports()
    elif args.check == "backend":
        payload = {**check_backend_health_placeholder(), **launch_backend(dry_run=True)}
    elif args.check == "frontend":
        payload = {**check_frontend_health_placeholder(), **launch_frontend(dry_run=True)}
    elif args.check == "browser":
        payload = open_browser(dry_run=True)
    elif args.check == "safety":
        payload = build_local_launcher_safety_summary()
    elif args.check == "logs":
        payload = {"logs": read_recent_launcher_logs(), **boundary()}
    elif args.check == "status":
        payload = get_local_launcher_status()
    else:
        payload = summarize_local_launcher_result(run_local_launcher(dry_run=dry_run))

    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
