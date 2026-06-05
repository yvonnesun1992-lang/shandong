from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.system.health_check import run_system_health_check


REQUIRED_DEPENDENCIES = [
    "pandas",
    "numpy",
    "matplotlib",
    "streamlit",
    "yfinance",
    "akshare",
    "pytest",
]
REQUIRED_DIRECTORIES = [
    PROJECT_ROOT / "config",
    PROJECT_ROOT / "data" / "sample",
    PROJECT_ROOT / "data" / "cache",
    PROJECT_ROOT / "reports" / "backtests",
    PROJECT_ROOT / "reports" / "daily",
    PROJECT_ROOT / "reports" / "workflow_runs",
]
REQUIRED_FILES = [
    PROJECT_ROOT / "config" / "settings.json",
    PROJECT_ROOT / "config" / "watchlists.json",
    PROJECT_ROOT / "config" / "paper_portfolio.json",
    PROJECT_ROOT / "data" / "sample" / "us_NVDA.csv",
    PROJECT_ROOT / "data" / "sample" / "cn_300308.csv",
]
NEXT_STEPS = [
    "python -m pip install -r requirements.txt",
    "python -m pytest",
    "streamlit run app/main.py",
]


def relative_key(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def make_check(name: str, status: str, message: str, details: dict | None = None) -> dict:
    return {
        "name": name,
        "status": status,
        "message": message,
        "details": details or {},
    }


def check_python_version(version_info=sys.version_info) -> dict:
    version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    if (version_info.major, version_info.minor) < (3, 11):
        return make_check(
            "python_version",
            "error",
            f"Python {version} is too old. Python 3.11+ is required.",
            {"version": version},
        )
    return make_check("python_version", "ok", f"Python {version} is supported.", {"version": version})


def check_dependencies(
    dependencies: list[str] | None = None,
    importer: Callable[[str], object] = importlib.import_module,
) -> dict:
    dependency_names = dependencies or REQUIRED_DEPENDENCIES
    missing = []
    loaded = []
    for dependency in dependency_names:
        try:
            importer(dependency)
            loaded.append(dependency)
        except ImportError:
            missing.append(dependency)

    details = {"loaded": loaded, "missing": missing}
    if missing:
        return make_check(
            "dependencies",
            "error",
            "Some Python dependencies are missing. Run: python -m pip install -r requirements.txt",
            details,
        )
    return make_check("dependencies", "ok", "All required Python dependencies can be imported.", details)


def check_required_directories(directories: list[Path] | None = None) -> dict:
    directory_paths = directories or REQUIRED_DIRECTORIES
    missing = [relative_key(path) for path in directory_paths if not path.is_dir()]
    if missing:
        return make_check("required_directories", "warning", "Some required directories are missing.", {"missing": missing})
    return make_check("required_directories", "ok", "All required directories exist.")


def check_required_files(files: list[Path] | None = None) -> dict:
    file_paths = files or REQUIRED_FILES
    missing = [relative_key(path) for path in file_paths if not path.is_file()]
    if missing:
        return make_check("required_files", "warning", "Some required files are missing.", {"missing": missing})
    return make_check("required_files", "ok", "All required files exist.")


def run_doctor(health_check_func: Callable[[], dict] = run_system_health_check) -> dict:
    checks = [
        check_python_version(),
        check_dependencies(),
        check_required_directories(),
        check_required_files(),
    ]
    try:
        health_result = health_check_func()
        checks.append(
            make_check(
                "system_health",
                health_result.get("overall_status", "error"),
                f"System health check completed with status: {health_result.get('overall_status', 'unknown')}",
                health_result,
            )
        )
    except Exception as error:
        checks.append(
            make_check(
                "system_health",
                "error",
                f"System health check failed: {error}",
                {"error_type": type(error).__name__},
            )
        )

    error_count = sum(1 for check in checks if check["status"] == "error")
    warning_count = sum(1 for check in checks if check["status"] == "warning")
    ok_count = sum(1 for check in checks if check["status"] == "ok")
    if error_count:
        overall_status = "error"
    elif warning_count:
        overall_status = "warning"
    else:
        overall_status = "ok"
    return {
        "overall_status": overall_status,
        "checks": checks,
        "ok_count": ok_count,
        "warning_count": warning_count,
        "error_count": error_count,
        "next_steps": NEXT_STEPS,
    }


def print_doctor_result(result: dict) -> None:
    print(f"System doctor status: {result['overall_status'].upper()}")
    for check in result["checks"]:
        print(f"[{check['status'].upper()}] {check['name']}: {check['message']}")

    if result["overall_status"] != "ok":
        print("\nSuggested next steps:")
        for step in result["next_steps"]:
            print(f"- {step}")


def main() -> int:
    result = run_doctor()
    print_doctor_result(result)
    if result["overall_status"] == "error":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
