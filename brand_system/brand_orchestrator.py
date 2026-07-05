from __future__ import annotations

from pathlib import Path

from brand_system.brand_safety_validator import build_brand_safety_summary
from brand_system.design_system import get_design_system
from config.v5_brand_system_config import get_brand_assets, get_brand_status
from runtime.brand_consistency_check import run_brand_consistency_check


def build_brand_system_status() -> dict:
    assets = get_brand_assets()
    consistency = run_brand_consistency_check()
    safety = build_brand_safety_summary()
    logo_path = Path("web/frontend/public/brand/shandong-quant-logo.png")
    readme_text = Path("README.md").read_text(encoding="utf-8", errors="ignore") if Path("README.md").exists() else ""
    cli_text = Path("scripts/run_v544_brand_system.py").read_text(encoding="utf-8", errors="ignore") if Path("scripts/run_v544_brand_system.py").exists() else ""
    warnings = []
    warnings.extend(consistency.get("warnings", []))
    warnings.extend(safety.get("warnings", []))
    return {
        "version": "V5.44",
        "brand_system_only": True,
        "assets": assets,
        "design_system": get_design_system(),
        "branding_applied": True,
        "ui_consistency_check": consistency,
        "logo_consistency_check": {
            "logo_exists": logo_path.exists(),
            "logo_asset": assets["logo_asset"],
            "logo_style": assets["brand_logo"],
        },
        "cli_branding_check": {
            "banner_present": "Shandong Quantitative System" in cli_text and "Institutional Quant Platform" in cli_text,
        },
        "readme_branding_check": {
            "readme_branding_present": "Shandong Quantitative System" in readme_text,
            "safety_statement_present": "no broker" in readme_text.lower() and "no real money" in readme_text.lower(),
        },
        "safety": safety,
        "status": get_brand_status(),
        "warnings": warnings,
        "verdict": "PASS" if consistency.get("passed") and safety.get("safe") and logo_path.exists() else "WARNING",
    }
