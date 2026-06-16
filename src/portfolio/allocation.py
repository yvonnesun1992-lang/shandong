from __future__ import annotations

from math import floor


RESEARCH_DISCLAIMER = "仅供投资研究，不构成投资建议，不代表未来收益。"

# V1.18 raw refresh marker: keep allocation.py as real multiline Python.
# V1.18 formatting verification marker 6: remote raw must stay multiline.


def _normalize_symbols(symbols: list[str]) -> list[str]:
    normalized = []
    seen = set()
    for symbol in symbols:
        clean_symbol = str(symbol).strip().upper()
        if clean_symbol and clean_symbol not in seen:
            normalized.append(clean_symbol)
            seen.add(clean_symbol)
    return normalized


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _capped_score_weights(
    eligible_scores: dict[str, float],
    total_weight: float,
    max_position_pct: float,
) -> dict[str, float]:
    weights = {symbol: 0.0 for symbol in eligible_scores}
    remaining_symbols = set(eligible_scores)
    remaining_weight = total_weight

    while remaining_symbols and remaining_weight > 0:
        score_sum = sum(max(eligible_scores[symbol], 0.0) for symbol in remaining_symbols)
        if score_sum <= 0:
            even_weight = remaining_weight / len(remaining_symbols)
            for symbol in list(remaining_symbols):
                add_weight = min(even_weight, max_position_pct - weights[symbol])
                weights[symbol] += max(add_weight, 0.0)
            break

        capped_this_round = set()
        distributed = 0.0
        for symbol in list(remaining_symbols):
            proposed = remaining_weight * max(eligible_scores[symbol], 0.0) / score_sum
            room = max_position_pct - weights[symbol]
            add_weight = min(proposed, room)
            weights[symbol] += max(add_weight, 0.0)
            distributed += max(add_weight, 0.0)
            if weights[symbol] >= max_position_pct - 1e-12:
                capped_this_round.add(symbol)

        if distributed <= 1e-12:
            break

        remaining_weight -= distributed
        remaining_symbols -= capped_this_round

        if not capped_this_round:
            break

    return weights


def build_allocation_plan(
    symbols: list[str],
    scores: dict[str, float],
    prices: dict[str, float],
    current_positions: dict[str, float] | None = None,
    portfolio_value: float = 100000.0,
    max_position_pct: float = 0.2,
    min_score: float = 60.0,
    cash_buffer_pct: float = 0.1,
) -> dict:
    """Build a research-only target allocation plan from local scores and prices."""
    warnings = [RESEARCH_DISCLAIMER]
    failed_symbols: list[dict] = []
    current_positions = current_positions or {}

    portfolio_value = float(portfolio_value)
    max_position_pct = float(max_position_pct)
    min_score = float(min_score)
    cash_buffer_pct = float(cash_buffer_pct)

    if portfolio_value <= 0:
        raise ValueError("portfolio_value must be positive.")
    if max_position_pct <= 0 or max_position_pct > 1:
        raise ValueError("max_position_pct must be greater than 0 and less than or equal to 1.")
    if cash_buffer_pct < 0 or cash_buffer_pct >= 1:
        raise ValueError("cash_buffer_pct must be greater than or equal to 0 and less than 1.")

    clean_symbols = _normalize_symbols(symbols)
    investable_weight = 1.0 - cash_buffer_pct
    investable_value = portfolio_value * investable_weight
    cash_buffer = portfolio_value * cash_buffer_pct

    if not clean_symbols:
        warnings.append("股票池为空，无法生成目标仓位。")
        return {
            "summary": {
                "portfolio_value": portfolio_value,
                "investable_value": investable_value,
                "cash_buffer": cash_buffer,
                "selected_symbols": 0,
                "max_position_pct": max_position_pct,
                "disclaimer": RESEARCH_DISCLAIMER,
            },
            "allocation": [],
            "warnings": warnings,
            "failed_symbols": failed_symbols,
        }

    if cash_buffer_pct < 0.05:
        warnings.append("现金缓冲较低，研究时应关注流动性和回撤风险。")

    valid_rows: dict[str, dict] = {}
    eligible_scores: dict[str, float] = {}

    for symbol in clean_symbols:
        price = _safe_float(prices.get(symbol))
        score = _safe_float(scores.get(symbol))
        current_shares = max(_safe_float(current_positions.get(symbol)), 0.0)

        if price <= 0:
            failed_symbols.append({"symbol": symbol, "error": "Missing or invalid price."})
            warnings.append(f"{symbol} 价格缺失或无效，已跳过。")
            continue

        valid_rows[symbol] = {
            "symbol": symbol,
            "score": score,
            "price": price,
            "current_shares": current_shares,
            "current_value": current_shares * price,
        }
        if score >= min_score:
            eligible_scores[symbol] = score

    if not eligible_scores:
        warnings.append("没有股票达到最低分数要求，目标仓位均为 0。")

    if eligible_scores and len(eligible_scores) <= 2:
        warnings.append("入选股票数量较少，组合集中度风险较高。")

    max_possible_weight = len(eligible_scores) * max_position_pct
    target_weight_pool = min(investable_weight, max_possible_weight)
    if eligible_scores and max_possible_weight < investable_weight:
        warnings.append("单股最大仓位限制较严格，无法完全使用可投资金额。")

    target_weights = _capped_score_weights(eligible_scores, target_weight_pool, max_position_pct)

    allocation = []
    for symbol in clean_symbols:
        row = valid_rows.get(symbol)
        if not row:
            continue
        target_weight = target_weights.get(symbol, 0.0)
        target_value = portfolio_value * target_weight
        target_shares = floor(target_value / row["price"]) if row["price"] > 0 else 0
        current_value = row["current_value"]
        allocation.append(
            {
                "symbol": symbol,
                "score": row["score"],
                "price": row["price"],
                "target_weight": target_weight,
                "target_value": target_value,
                "target_shares": int(target_shares),
                "current_shares": row["current_shares"],
                "current_value": current_value,
                "difference_value": target_value - current_value,
                "disclaimer": RESEARCH_DISCLAIMER,
            }
        )

    return {
        "summary": {
            "portfolio_value": portfolio_value,
            "investable_value": investable_value,
            "cash_buffer": cash_buffer,
            "selected_symbols": len(eligible_scores),
            "max_position_pct": max_position_pct,
            "disclaimer": RESEARCH_DISCLAIMER,
        },
        "allocation": allocation,
        "warnings": warnings,
        "failed_symbols": failed_symbols,
    }
