from __future__ import annotations


BRAND_COLORS = {
    "primary": "#0B1F3B",
    "secondary": "#C8A24A",
    "background": "#061525",
    "surface": "#0E2746",
    "surface_soft": "#132F52",
    "text": "#F6F2E8",
    "muted": "#B9C2D0",
    "line": "#24415F",
    "danger": "#D96C5F",
    "warning": "#C8A24A",
    "success": "#6BBF9A",
}

TYPOGRAPHY = {
    "font_family": "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
    "heading_weight": 850,
    "body_weight": 500,
    "letter_spacing": 0,
}

SPACING = {
    "page_padding": "32px",
    "card_padding": "18px",
    "grid_gap": "16px",
    "radius": "8px",
}

STYLE_RULES = [
    "Institutional / Bloomberg-like UI",
    "No playful UI",
    "No neon or cyberpunk theme",
    "No cartoon style",
    "High contrast financial dashboard style",
]

COMPONENT_RULES = [
    "Cards use subtle radius and sharp financial-dashboard contrast",
    "Buttons are minimal and solid",
    "Charts use gold and blue theme tokens",
    "Status labels stay professional and concise",
]


def get_design_system() -> dict:
    return {
        "theme": "institutional_quant",
        "colors": BRAND_COLORS,
        "typography": TYPOGRAPHY,
        "spacing": SPACING,
        "style_rules": STYLE_RULES,
        "component_rules": COMPONENT_RULES,
    }
