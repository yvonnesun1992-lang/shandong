from __future__ import annotations


RESEARCH_DISCLAIMER = "仅供投资研究，不构成投资建议，不代表未来收益。"


def _safe_float(value, default: float | None = None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clean_symbol(value) -> str:
    return str(value or "").strip().upper()


def _status_from_flags(has_fail: bool, has_warn: bool) -> str:
    if has_fail:
        return "fail"
    if has_warn:
        return "warn"
    return "pass"


def _risk_level(checks: list[dict]) -> str:
    fail_count = sum(1 for check in checks if check.get("status") == "fail")
    warn_count = sum(1 for check in checks if check.get("status") == "warn")
    if fail_count >= 2 or (fail_count >= 1 and warn_count >= 2):
        return "High"
    if fail_count >= 1 or warn_count >= 2:
        return "Medium"
    return "Low"


def build_risk_control_report(
    allocation_rows: list[dict],
    portfolio_value: float = 100000.0,
    cash_buffer_pct: float = 0.1,
    max_position_pct: float = 0.2,
    max_top3_pct: float = 0.5,
    min_positions: int = 5,
) -> dict:
    """Build a research-only risk report from target allocation rows."""
    warnings = [RESEARCH_DISCLAIMER]
    position_risks: list[dict] = []
    checks: list[dict] = []
    valid_positions: list[dict] = []
    zero_weight_symbols: list[str] = []
    overweight_symbols: list[str] = []

    portfolio_value = _safe_float(portfolio_value, 0.0) or 0.0
    cash_buffer_pct = _safe_float(cash_buffer_pct, 0.0) or 0.0
    max_position_pct = _safe_float(max_position_pct, 0.0) or 0.0
    max_top3_pct = _safe_float(max_top3_pct, 0.0) or 0.0
    min_positions = max(int(min_positions or 0), 0)

    if portfolio_value <= 0:
        warnings.append("组合总金额无效，风险报告仅返回提示，不进行仓位比例判断。")
        checks.append(
            {
                "name": "数据质量风险",
                "status": "fail",
                "message": "组合总金额需要大于 0。",
            }
        )

    if not allocation_rows:
        warnings.append("目标仓位数据为空，无法判断仓位集中度。")
        checks.append(
            {
                "name": "数据质量风险",
                "status": "fail",
                "message": "没有可用于风险检查的目标仓位。",
            }
        )

    for index, row in enumerate(allocation_rows or [], start=1):
        symbol = _clean_symbol(row.get("symbol"))
        if not symbol:
            warnings.append(f"第 {index} 行缺少 symbol，已跳过。")
            continue

        target_weight = _safe_float(row.get("target_weight"))
        target_value = _safe_float(row.get("target_value"))
        if target_weight is None and target_value is None:
            warnings.append(f"{symbol} 缺少 target_weight 和 target_value，已跳过。")
            continue
        if target_weight is None:
            if portfolio_value > 0 and target_value is not None:
                target_weight = target_value / portfolio_value
            else:
                warnings.append(f"{symbol} 缺少 target_weight，且组合总金额无效，已跳过。")
                continue
        if target_value is None:
            target_value = portfolio_value * target_weight if portfolio_value > 0 else 0.0

        target_weight = max(float(target_weight), 0.0)
        target_value = max(float(target_value), 0.0)
        position = {
            "symbol": symbol,
            "target_weight": target_weight,
            "target_value": target_value,
        }
        valid_positions.append(position)

        if target_weight <= 0:
            zero_weight_symbols.append(symbol)
        if max_position_pct > 0 and target_weight > max_position_pct:
            overweight_symbols.append(symbol)
            position_risks.append(
                {
                    "symbol": symbol,
                    "target_weight": target_weight,
                    "target_value": target_value,
                    "risk": "单股仓位超过限制",
                }
            )

    active_positions = [position for position in valid_positions if position["target_weight"] > 0]
    sorted_positions = sorted(active_positions, key=lambda position: position["target_weight"], reverse=True)
    total_target_value = sum(position["target_value"] for position in valid_positions)
    invested_pct = total_target_value / portfolio_value if portfolio_value > 0 else 0.0
    cash_buffer_value = max(portfolio_value - total_target_value, 0.0) if portfolio_value > 0 else 0.0
    largest_position_pct = sorted_positions[0]["target_weight"] if sorted_positions else 0.0
    top3_position_pct = sum(position["target_weight"] for position in sorted_positions[:3])
    number_of_positions = len(active_positions)

    if overweight_symbols:
        warnings.append("存在单股仓位超过限制的股票。")
    checks.append(
        {
            "name": "仓位风险",
            "status": "fail" if overweight_symbols else "pass",
            "message": (
                f"单股最大仓位 {largest_position_pct:.2%}，限制为 {max_position_pct:.2%}。"
                if max_position_pct > 0
                else "单股最大仓位限制无效，请检查参数。"
            ),
        }
    )

    top3_fail = max_top3_pct > 0 and top3_position_pct > max_top3_pct
    if top3_fail:
        warnings.append("前三大持仓占比过高，组合集中度风险较高。")
    checks.append(
        {
            "name": "集中度风险",
            "status": "fail" if top3_fail else "pass",
            "message": (
                f"前三大持仓占比 {top3_position_pct:.2%}，上限为 {max_top3_pct:.2%}。"
                if max_top3_pct > 0
                else "前三大持仓上限无效，请检查参数。"
            ),
        }
    )

    too_few_positions = number_of_positions < min_positions
    if too_few_positions:
        warnings.append("持仓数量少于最低分散要求，分散度不足。")
    checks.append(
        {
            "name": "分散度风险",
            "status": "warn" if too_few_positions else "pass",
            "message": f"当前有效持仓 {number_of_positions} 个，最低建议 {min_positions} 个。",
        }
    )

    low_cash_buffer = cash_buffer_pct < 0.05
    if low_cash_buffer:
        warnings.append("现金缓冲偏低，遇到回撤或数据延迟时调整空间较小。")
    checks.append(
        {
            "name": "现金缓冲风险",
            "status": "warn" if low_cash_buffer else "pass",
            "message": f"设置的现金缓冲为 {cash_buffer_pct:.2%}，当前估算现金为 {cash_buffer_value:,.2f}。",
        }
    )

    invalid_data_warning = bool([warning for warning in warnings if "缺少" in warning or "已跳过" in warning])
    checks.append(
        {
            "name": "数据质量风险",
            "status": _status_from_flags(portfolio_value <= 0 or not allocation_rows, invalid_data_warning),
            "message": "已检查目标仓位字段完整性；缺失字段会被跳过并记录提示。",
        }
    )

    checks.append(
        {
            "name": "回撤风险提示",
            "status": "warn" if top3_fail or low_cash_buffer else "pass",
            "message": "本报告不预测未来回撤；请结合组合回测最大回撤和现金缓冲一起判断。",
        }
    )

    risk_level = _risk_level(checks)

    return {
        "summary": {
            "portfolio_value": portfolio_value,
            "total_target_value": total_target_value,
            "cash_buffer_value": cash_buffer_value,
            "invested_pct": invested_pct,
            "largest_position_pct": largest_position_pct,
            "top3_position_pct": top3_position_pct,
            "number_of_positions": number_of_positions,
            "risk_level": risk_level,
            "disclaimer": RESEARCH_DISCLAIMER,
        },
        "position_risks": position_risks,
        "warnings": warnings,
        "checks": checks,
        "overweight_symbols": overweight_symbols,
        "zero_weight_symbols": zero_weight_symbols,
    }
