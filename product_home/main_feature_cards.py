from __future__ import annotations

from product_home.init import boundary


def build_main_feature_cards() -> list[dict]:
    cards = [
        ("Quant Research", "Generate and review local research reports.", "/strategy", "Ready", "Research"),
        ("Backtest", "Inspect local backtest and performance workflows.", "/reports", "Ready", "Backtest"),
        ("Paper Trading", "Review paper-only trading state and monitoring.", "/v5-live-paper", "Paper only", "Paper"),
        ("Risk Monitor", "Check risk controls and disabled real paths.", "/risk", "Ready", "Risk"),
        ("Local Launcher", "Open the V5.39 localhost launcher page.", "/v5-local-launcher", "Ready", "Launcher"),
        ("Read-Only Evidence Pack", "Review local read-only evidence without provider access.", "/v5-read-only-evidence-pack", "Review only", "Evidence"),
        ("System Logs", "Review local workflow and launcher activity.", "/admin", "Local only", "Logs"),
        ("Safety Boundary", "Confirm no broker, no sandbox API, and no real money.", "/v5-product-home", "Locked", "Safety"),
    ]
    return [
        {
            "title": title,
            "description": description,
            "route": route,
            "status": status,
            "user_friendly_label": label,
            **boundary(),
        }
        for title, description, route, status, label in cards
    ]
