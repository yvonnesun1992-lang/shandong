from __future__ import annotations

from pathlib import Path

from brand_system.design_system import BRAND_COLORS


ALLOWED_COLORS = {value.lower() for value in BRAND_COLORS.values()} | {
    "#ffffff",
    "#000000",
    "transparent",
}


def run_brand_consistency_check() -> dict:
    warnings: list[str] = []
    style_path = Path("web/frontend/app/styles.css")
    shell_path = Path("web/frontend/app/components/ProductionShell.tsx")
    logo_component_path = Path("web/frontend/app/components/BrandLogo.tsx")
    home_path = Path("web/frontend/app/page.tsx")
    logo_path = Path("web/frontend/public/brand/shandong-quant-logo.png")

    style_text = style_path.read_text(encoding="utf-8", errors="ignore") if style_path.exists() else ""
    shell_text = shell_path.read_text(encoding="utf-8", errors="ignore") if shell_path.exists() else ""
    logo_component_text = logo_component_path.read_text(encoding="utf-8", errors="ignore") if logo_component_path.exists() else ""
    home_text = home_path.read_text(encoding="utf-8", errors="ignore") if home_path.exists() else ""

    required_tokens = ["--bg", "--panel", "--accent", "--gold", "--nav", "--ink"]
    missing_tokens = [token for token in required_tokens if token not in style_text]
    if missing_tokens:
        warnings.append(f"missing brand css tokens: {', '.join(missing_tokens)}")

    if "/brand/shandong-quant-logo.png" not in shell_text + logo_component_text + home_text:
        warnings.append("brand logo asset is not referenced in frontend shell or home")
    if "Shandong Quantitative System" not in shell_text + home_text:
        warnings.append("brand name is not visible in frontend shell or home")
    if not logo_path.exists():
        warnings.append("brand logo asset is missing")

    non_brand_theme_terms = ["cyberpunk", "cartoon", "playful", "neon"]
    found_non_brand_terms = [term for term in non_brand_theme_terms if term in style_text.lower()]
    if found_non_brand_terms:
        warnings.append(f"non-brand theme terms found: {', '.join(found_non_brand_terms)}")

    return {
        "passed": not warnings,
        "brand_theme": "institutional_quant",
        "checked_files": [style_path.as_posix(), shell_path.as_posix(), logo_component_path.as_posix(), home_path.as_posix()],
        "required_tokens": required_tokens,
        "logo_asset": logo_path.as_posix(),
        "warnings": warnings,
    }
