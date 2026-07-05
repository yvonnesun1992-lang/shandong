from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


LOCKED_FALSE_KEYS = [
    "brand_runtime_enabled",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
    "balance_read_enabled",
    "position_read_enabled",
    "order_preview_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def test_brand_config_locked_and_blocks_env(monkeypatch):
    from config.v5_brand_system_config import get_brand_assets, get_brand_mode, get_brand_status

    status = get_brand_status()
    assets = get_brand_assets()
    assert get_brand_mode() == "brand_system_only"
    assert status["brand_mode"] == "brand_system_only"
    assert status["brand_system_only"] is True
    assert status["paper_trading"] is True
    assert assets["brand_name"] == "Shandong Quantitative System"
    assert assets["brand_name_cn"] == "山洞量化系统"
    assert assets["brand_logo"] == "gold_mountain_candlestick_style"
    assert assets["primary_color"] == "deep_navy"
    assert assets["accent_color"] == "gold"
    assert assets["theme"] == "institutional_quant"
    for key in LOCKED_FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_BRAND_SYSTEM_MODE", "production")
    for env_name in [
        "SHANDONG_V5_ENABLE_BRAND_RUNTIME",
        "SHANDONG_V5_ENABLE_SANDBOX_API",
        "SHANDONG_V5_ENABLE_SECRET_READ",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION",
        "SHANDONG_V5_ENABLE_REAL_MONEY",
    ]:
        monkeypatch.setenv(env_name, "true")
    blocked = get_brand_status()
    warnings = " | ".join(blocked["warnings"]).lower()
    assert blocked["brand_mode"] == "brand_system_only"
    assert "mode override requested but blocked in v5.44" in warnings
    assert "brand runtime requested but blocked in v5.44" in warnings
    assert "sandbox api requested but blocked in v5.44" in warnings
    assert "secret read requested but blocked in v5.44" in warnings
    assert "account read requested but blocked in v5.44" in warnings
    assert "order submission requested but blocked in v5.44" in warnings
    assert "real money requested but blocked in v5.44" in warnings
    for key in LOCKED_FALSE_KEYS:
        assert blocked[key] is False
    assert _safe_payload(blocked)


def test_brand_modules_assets_frontend_and_docs():
    from brand_system.brand_orchestrator import build_brand_system_status
    from brand_system.brand_safety_validator import build_brand_safety_summary, validate_brand_safety
    from brand_system.design_system import get_design_system
    from runtime.brand_consistency_check import run_brand_consistency_check

    design = get_design_system()
    consistency = run_brand_consistency_check()
    safety = build_brand_safety_summary()
    summary = build_brand_system_status()

    assert design["theme"] == "institutional_quant"
    assert design["colors"]["primary"] == "#0B1F3B"
    assert design["colors"]["secondary"] == "#C8A24A"
    assert consistency["passed"] is True
    assert safety["safe"] is True
    assert validate_brand_safety({"broker_connected": True})["safe"] is False
    assert summary["branding_applied"] is True
    assert summary["logo_consistency_check"]["logo_exists"] is True
    assert summary["cli_branding_check"]["banner_present"] is True
    assert summary["readme_branding_check"]["readme_branding_present"] is True

    required_files = [
        "web/frontend/public/brand/shandong-quant-logo.png",
        "brand_system/assets/shandong-quant-logo.png",
        "brand_system/BRAND_GUIDE.md",
        "docs/V5_BRAND_SYSTEM.md",
        "web/frontend/app/components/BrandLogo.tsx",
    ]
    for file_name in required_files:
        assert Path(file_name).exists()

    frontend_text = "\n".join(
        Path(path).read_text(encoding="utf-8", errors="ignore")
        for path in [
                "web/frontend/app/page.tsx",
                "web/frontend/app/components/BrandLogo.tsx",
                "web/frontend/app/components/ProductionShell.tsx",
            "web/frontend/app/components/LoadingState.tsx",
            "web/frontend/app/styles.css",
        ]
    )
    assert "Shandong Quantitative System" in frontend_text
    assert "山洞量化系统" in frontend_text
    assert "/brand/shandong-quant-logo.png" in frontend_text
    assert "#061525" in frontend_text
    assert "#c8a24a" in frontend_text.lower()
    assert "cyberpunk" not in frontend_text.lower()
    assert "cartoon" not in frontend_text.lower()
    assert _safe_text(frontend_text)


def test_brand_api_and_cli_are_available():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    for path in [
        "/api/v5/brand-system/status",
        "/api/v5/brand-system/design",
        "/api/v5/brand-system/consistency",
        "/api/v5/brand-system/safety",
        "/api/v5/brand-system/summary",
    ]:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload, default=str).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "brand_system" in text or "brand system" in text
        assert "shandong quantitative system" in text or "institutional_quant" in text
        assert _safe_payload(payload)

    completed = subprocess.run(
        [sys.executable, "scripts/run_v544_brand_system.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert "Shandong Quantitative System" in completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["brand_system_only"] is True
    assert payload["verdict"] == "PASS"
    assert _safe_payload(payload)


def test_brand_does_not_touch_trading_logic_or_real_paths():
    changed_scope = "\n".join(
        Path(path).read_text(encoding="utf-8", errors="ignore")
        for path in [
            "config/v5_brand_system_config.py",
            "brand_system/brand_orchestrator.py",
            "runtime/brand_consistency_check.py",
            "scripts/run_v544_brand_system.py",
        ]
    )
    assert "place_order(" not in changed_scope
    assert "submit_real_order" not in changed_scope
    assert "alpaca_trade_api" not in changed_scope
    assert "ib_insync" not in changed_scope
    assert "sk-" not in changed_scope
    assert "eval(" not in changed_scope
    assert "exec(" not in changed_scope


def _safe_payload(payload: object) -> bool:
    return _safe_text(json.dumps(payload, default=str).lower())


def _safe_text(text: str) -> bool:
    lowered = text.lower()
    blocked = [
        "api_key=demo",
        "secret_value=demo",
        "token=demo",
        "password=demo",
        "authorization: bearer",
        "real_order_id_",
        "real_account_id",
        "raw provider payload",
        "paper-api.",
        "api.alpaca.",
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "sandbox_api_enabled\": true",
        "secret_read_enabled\": true",
        "account_read_enabled\": true",
        "balance_read_enabled\": true",
        "position_read_enabled\": true",
        "order_submission_enabled\": true",
        "broker_connected\": true",
        "real_money_enabled\": true",
    ]
    return not any(term in lowered for term in blocked)
