from __future__ import annotations

from pathlib import Path

from product_home.product_home_orchestrator import build_product_home_dashboard
from product_home.product_home_safety_validator import build_product_home_safety_summary


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "reports" / "v5_40_product_home_dashboard_report.md"


def generate_product_home_report() -> dict:
    dashboard = build_product_home_dashboard()
    safety = build_product_home_safety_summary()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# V5.40 Product Home Dashboard Report",
        "",
        "- product home mode: product_home_only",
        f"- verdict: {dashboard['verdict']}",
        f"- system health: {dashboard['system_health']}",
        f"- runtime visible: {dashboard['runtime_visible']}",
        f"- feature cards: {len(dashboard['feature_cards'])}",
        f"- safety validation: {'PASS' if safety['safe'] else 'FAIL'}",
        "",
        "## Safety Boundary",
        "",
        "- Current page is a Product Home Dashboard.",
        "- It does not connect to a real broker.",
        "- It does not connect to a sandbox API.",
        "- It does not read secrets.",
        "- It does not read accounts, balances, or positions.",
        "- It does not submit orders.",
        "- It does not connect to real money.",
        "",
        "## Missing Product Requirements",
        "",
        "- Formal packaged desktop installer remains future work.",
        "- Real production identity, broker, and payment integrations remain disabled.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"path": "reports/v5_40_product_home_dashboard_report.md", "dashboard": dashboard, "safety": safety, "product_home_only": True}
