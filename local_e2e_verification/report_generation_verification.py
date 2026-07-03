from __future__ import annotations

from pathlib import Path

from local_e2e_verification.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "reports" / "v5_41_local_e2e_verification_report.md"


def generate_local_e2e_verification_report() -> dict:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# V5.41 Local End-to-End Run Verification Report",
        "",
        "- local launcher verification: included",
        "- backend smoke test: TestClient only",
        "- frontend smoke test: file-level only",
        "- API smoke test matrix: product home and local launcher endpoints",
        "- log write verification: reports/local_launcher only",
        "- safety boundary verification: locked",
        "",
        "## Safety Boundary",
        "",
        "- Current stage is local e2e verification only.",
        "- It does not connect to a real broker.",
        "- It does not connect to a sandbox API.",
        "- It does not read secrets.",
        "- It does not read accounts, balances, or positions.",
        "- It does not submit orders.",
        "- It does not connect to real money.",
        "",
        "## Missing Local Run Requirements",
        "",
        "- Manual browser inspection remains optional.",
        "- Packaged desktop installers remain future work.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"report_generated": True, "path": "reports/v5_41_local_e2e_verification_report.md", **boundary()}


def summarize_report_generation(result: dict) -> dict:
    return {"report_generated": result.get("report_generated", False), "path": result.get("path", ""), "warnings": result.get("warnings", []), "errors": result.get("errors", []), **boundary()}
