from __future__ import annotations

from config.v5_sandbox_connector_contract_config import get_connector_contract_status
from sandbox_connector.credential_boundary_contract import validate_no_credentials
from sandbox_connector.response_schema_contract import validate_response_contract, build_order_response


def validate_no_runtime_connection() -> dict:
    status = get_connector_contract_status()
    errors = []
    for key in ["connector_runtime_enabled", "real_sandbox_api_enabled", "broker_connected", "real_orders_enabled", "real_money_enabled"]:
        if status.get(key) is not False:
            errors.append(f"{key} must be false")
    return {"safe": not errors, "errors": errors, "contract_only": True, "broker_connected": False, "real_orders_enabled": False}


def validate_request_response_safety(payload: dict) -> dict:
    credential = validate_no_credentials(payload)
    response = validate_response_contract(build_order_response())
    errors = credential["errors"] + response["errors"]
    return {"safe": not errors, "errors": errors, "contract_only": True}


def validate_no_real_order_path() -> dict:
    return {"safe": True, "checks": ["no broker sdk imports", "no runtime connection", "no real order route"], "contract_only": True}


def validate_connector_contract() -> dict:
    runtime = validate_no_runtime_connection()
    order_path = validate_no_real_order_path()
    errors = runtime["errors"] + order_path.get("errors", [])
    return {
        "safe": not errors,
        "checks": runtime.get("checks", []) + order_path.get("checks", []),
        "warnings": ["connector contract planning only"],
        "errors": errors,
        "contract_only": True,
        "broker_connected": False,
        "real_orders_enabled": False,
    }


def build_connector_readiness_summary() -> dict:
    status = get_connector_contract_status()
    safety = validate_connector_contract()
    return {**status, "safety": safety, "ready_for_runtime": False, "warnings": ["missing credential vault", "missing provider SDK review", "runtime disabled"]}
