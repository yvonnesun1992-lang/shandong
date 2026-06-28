from __future__ import annotations

from pathlib import Path

from broker_adapter.adapter_factory import build_factory_status
from broker_adapter.adapter_registry import build_default_registry
from broker_adapter.capability_matrix import build_capability_matrix
from broker_adapter.compatibility_layer import validate_contract_alignment, validate_interface_compatibility
from broker_adapter.safety_guard import build_safety_guard_status
from runtime.security_scan import scan_broker_adapter_outputs


REPORT_PATH = Path("reports/v5_15_broker_adapter_skeleton_report.md")


def build_broker_adapter_summary(test_adapter: str = "ibkr_skeleton") -> dict:
    registry = build_default_registry()
    capabilities = build_capability_matrix()
    compatibility = validate_interface_compatibility()
    alignment = validate_contract_alignment()
    safety = build_safety_guard_status()
    factory = build_factory_status(test_adapter)
    verdict = "PASS" if compatibility["compatible"] and alignment["aligned"] and safety["safe"] else "FAIL"
    return {
        "version": "V5.15",
        "summary": {
            "skeleton_only": True,
            "adapter_count": len(registry.list_adapters()),
            "real_connection": False,
            "real_orders": False,
            "paper_trading": True,
        },
        "registry": registry.as_dict(),
        "factory": factory,
        "capability_matrix": capabilities,
        "compatibility": compatibility,
        "alignment": alignment,
        "safety": safety,
        "missing_production_requirements": [
            "provider SDK review",
            "credential vault",
            "sandbox certification",
            "manual release approval",
            "production monitoring signoff",
        ],
        "verdict": verdict,
        "warnings": [] if verdict == "PASS" else ["adapter skeleton check failed"],
    }


def generate_broker_adapter_report(test_adapter: str = "ibkr_skeleton") -> dict:
    payload = build_broker_adapter_summary(test_adapter)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(payload), encoding="utf-8")
    scan = scan_broker_adapter_outputs(payload, REPORT_PATH)
    if not scan["safe"]:
        payload["verdict"] = "FAIL"
        payload.setdefault("warnings", []).append("safety scan found blocked output")
    return {
        "path": REPORT_PATH.as_posix(),
        "verdict": payload["verdict"],
        "summary": payload["summary"],
        "warnings": payload.get("warnings", []),
        "skeleton_only": True,
        "real_connection": False,
        "real_orders": False,
        "paper_trading": True,
    }


def _render_report(payload: dict) -> str:
    summary = payload["summary"]
    return f"""# V5.15 Broker Adapter Skeleton + Sandbox Bridge

Verdict: {payload["verdict"]}

## Adapter Architecture

- Alpha Engine to Paper Trading Engine to Broker Adapter Interface.
- V5.14 mock connector remains local mock only.
- V5.15 adapter skeleton defines future broker adapter shapes.

## Registry Status

- Adapter count: {summary["adapter_count"]}
- Skeleton only: {summary["skeleton_only"]}

## Safety Guard Status

- Real connection: false
- Real orders: false
- Paper trading: true
- Current stage: broker adapter skeleton only.

## Missing Production Requirements

- Provider SDK review.
- Credential vault.
- Sandbox certification.
- Manual release approval.
- Production monitoring signoff.

## Boundary

- Current stage is not connected to a real broker.
- Current stage is not connected to sandbox API.
- Current stage does not trade real money.
- Current stage is not a production trading system.
"""
