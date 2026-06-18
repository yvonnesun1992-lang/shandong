from __future__ import annotations

from typing import Any

import pandas as pd


RESEARCH_DISCLAIMER = "仅供投资研究，不构成投资建议，不代表未来收益。"


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clean_period_result(result: dict[str, Any], default_name: str) -> dict[str, Any]:
    status = str(result.get("status", "success")).strip().lower() or "success"
    return {
        "period_name": str(result.get("period_name", default_name)).strip() or default_name,
        "total_return": _safe_float(result.get("total_return")),
        "annualized_return": _safe_float(result.get("annualized_return")),
        "max_drawdown": _safe_float(result.get("max_drawdown")),
        "number_of_trades": int(_safe_float(result.get("number_of_trades"), 0.0)),
        "final_portfolio_value": _safe_float(result.get("final_portfolio_value")),
        "status": status,
        "error": str(result.get("error", "")).strip(),
    }


def _return_decay(train_total_return: float, test_total_return: float) -> float:
    if train_total_return <= 0:
        return 0.0
    return max((train_total_return - test_total_return) / abs(train_total_return), 0.0)


def _overfit_risk_level(
    train_result: dict,
    test_result: dict,
    return_decay: float,
    drawdown_worsening: float,
    test_trade_sample_ok: bool,
) -> str:
    if train_result["status"] != "success" or test_result["status"] != "success":
        return "High"
    if test_result["total_return"] < 0 and train_result["total_return"] > 0:
        return "High"
    if return_decay > 0.75 or drawdown_worsening > 0.15:
        return "High"
    if return_decay > 0.5 or drawdown_worsening > 0.08 or not test_trade_sample_ok:
        return "Medium"
    return "Low"


def build_out_of_sample_report(
    train_result: dict,
    test_result: dict,
    min_test_trades: int = 3,
) -> dict:
    """Analyze train and out-of-sample backtest summaries without changing strategy logic."""
    min_test_trades = max(int(min_test_trades or 0), 0)
    warnings = [RESEARCH_DISCLAIMER]
    train = _clean_period_result(train_result or {}, "Train")
    test = _clean_period_result(test_result or {}, "Out-of-sample")

    train_total_return = train["total_return"]
    test_total_return = test["total_return"]
    decay = _return_decay(train_total_return, test_total_return)
    train_max_drawdown = train["max_drawdown"]
    test_max_drawdown = test["max_drawdown"]
    drawdown_worsening = max(abs(test_max_drawdown) - abs(train_max_drawdown), 0.0)
    train_trades = train["number_of_trades"]
    test_trades = test["number_of_trades"]
    test_trade_sample_ok = test_trades >= min_test_trades
    overfit_risk_level = _overfit_risk_level(train, test, decay, drawdown_worsening, test_trade_sample_ok)

    if train["status"] != "success":
        warnings.append("训练区间回测失败，无法可靠判断训练表现。")
    if test["status"] != "success":
        warnings.append("样本外测试区间回测失败，过拟合风险较高。")
    if test_total_return < 0 and train_total_return > 0:
        warnings.append("训练区间为正收益，但样本外测试为负收益，需警惕过拟合风险。")
    if decay > 0.5:
        warnings.append("样本外收益相对训练区间明显衰减。")
    if drawdown_worsening > 0.08:
        warnings.append("样本外最大回撤明显比训练区间更差。")
    if not test_trade_sample_ok:
        warnings.append("样本外交易次数较少，样本数量不足。")

    checks = [
        {
            "name": "训练区间表现",
            "status": "pass" if train["status"] == "success" else "fail",
            "message": f"训练区间收益 {train_total_return:.2%}，交易次数 {train_trades}。",
        },
        {
            "name": "样本外测试表现",
            "status": "pass" if test["status"] == "success" else "fail",
            "message": f"样本外收益 {test_total_return:.2%}，交易次数 {test_trades}。",
        },
        {
            "name": "收益衰减",
            "status": "fail" if decay > 0.75 else "warn" if decay > 0.5 else "pass",
            "message": f"收益衰减 {decay:.2%}。",
        },
        {
            "name": "回撤恶化",
            "status": "fail" if drawdown_worsening > 0.15 else "warn" if drawdown_worsening > 0.08 else "pass",
            "message": f"回撤恶化 {drawdown_worsening:.2%}。",
        },
        {
            "name": "过拟合风险",
            "status": "fail" if overfit_risk_level == "High" else "warn" if overfit_risk_level == "Medium" else "pass",
            "message": f"过拟合风险等级为 {overfit_risk_level}。",
        },
        {
            "name": "数据质量风险",
            "status": "warn" if not test_trade_sample_ok else "pass",
            "message": f"样本外交易次数 {test_trades}，最低建议 {min_test_trades}。",
        },
    ]

    return {
        "summary": {
            "train_total_return": train_total_return,
            "test_total_return": test_total_return,
            "return_decay": decay,
            "train_max_drawdown": train_max_drawdown,
            "test_max_drawdown": test_max_drawdown,
            "drawdown_worsening": drawdown_worsening,
            "train_trades": train_trades,
            "test_trades": test_trades,
            "test_trade_sample_ok": test_trade_sample_ok,
            "overfit_risk_level": overfit_risk_level,
            "disclaimer": RESEARCH_DISCLAIMER,
        },
        "period_results": [train, test],
        "warnings": warnings,
        "checks": checks,
    }


def _split_dataframe(data: pd.DataFrame, train_ratio: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    split_index = int(len(data) * train_ratio)
    train = data.iloc[:split_index].copy().reset_index(drop=True)
    test = data.iloc[split_index:].copy().reset_index(drop=True)
    return train, test


def split_train_test_data(
    data,
    train_ratio: float = 0.7,
) -> dict:
    """Split DataFrame or portfolio price-data dict into train and out-of-sample test sets."""
    warnings = []
    ratio = _safe_float(train_ratio, 0.7)
    if ratio < 0.5 or ratio > 0.9:
        warnings.append("train_ratio 已限制在 0.5 到 0.9 之间。")
        ratio = min(max(ratio, 0.5), 0.9)

    if isinstance(data, pd.DataFrame):
        if len(data) < 2:
            warnings.append("数据行数不足，无法切分训练和样本外测试区间。")
            return {"train": pd.DataFrame(), "test": pd.DataFrame(), "train_rows": 0, "test_rows": 0, "warnings": warnings}
        train, test = _split_dataframe(data, ratio)
        if train.empty or test.empty:
            warnings.append("切分后训练区间或样本外测试区间为空。")
        return {
            "train": train,
            "test": test,
            "train_rows": len(train),
            "test_rows": len(test),
            "warnings": warnings,
        }

    if isinstance(data, dict):
        train_data = {}
        test_data = {}
        train_rows = 0
        test_rows = 0
        for symbol, frame in data.items():
            if not isinstance(frame, pd.DataFrame) or len(frame) < 2:
                warnings.append(f"{symbol} 数据不足，已跳过切分。")
                continue
            train, test = _split_dataframe(frame, ratio)
            if train.empty or test.empty:
                warnings.append(f"{symbol} 切分后训练或测试区间为空，已跳过。")
                continue
            train_data[str(symbol)] = train
            test_data[str(symbol)] = test
            train_rows = max(train_rows, len(train))
            test_rows = max(test_rows, len(test))
        if not train_data or not test_data:
            warnings.append("没有可用于样本外测试的数据。")
        return {
            "train": train_data,
            "test": test_data,
            "train_rows": train_rows,
            "test_rows": test_rows,
            "warnings": warnings,
        }

    warnings.append("不支持的数据类型，无法切分训练和样本外测试区间。")
    return {"train": {}, "test": {}, "train_rows": 0, "test_rows": 0, "warnings": warnings}
