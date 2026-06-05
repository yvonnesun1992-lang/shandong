from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.system_doctor import print_doctor_result, run_doctor


def build_streamlit_command(python_executable: str | Path | None = None) -> list[str]:
    python_path = str(python_executable or sys.executable)
    return [python_path, "-m", "streamlit", "run", "app/main.py"]


def has_blocking_errors(doctor_result: dict) -> bool:
    return any(check["status"] == "error" for check in doctor_result.get("checks", []))


def main(
    doctor_func: Callable[[], dict] = run_doctor,
    runner: Callable[..., int] = subprocess.call,
) -> int:
    print("Running startup checks...")
    doctor_result = doctor_func()
    print_doctor_result(doctor_result)
    if has_blocking_errors(doctor_result):
        print("\nDashboard was not started because startup checks found errors.")
        print("Try: python -m pip install -r requirements.txt")
        print("Then: python -m pytest")
        return 1

    command = build_streamlit_command()
    print("\nStarting dashboard...")
    print("Command:", " ".join(command))
    try:
        return int(runner(command, cwd=PROJECT_ROOT))
    except FileNotFoundError as error:
        print(f"Failed to start dashboard: {error}")
        print("Try: python -m pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

