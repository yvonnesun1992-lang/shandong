from __future__ import annotations

import pandas as pd


STANDARD_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def _empty_report() -> dict:
    return {
        "is_valid": True,
        "warnings": [],
        "errors": [],
        "row_count": 0,
        "start_date": None,
        "end_date": None,
        "latest_close": None,
    }


def validate_ohlcv_data(data: pd.DataFrame, min_rows: int = 120) -> dict:
    """Validate a standard OHLCV table and return a beginner-readable report."""
    report = _empty_report()
    if data is None or data.empty:
        report["is_valid"] = False
        report["errors"].append("Data is empty.")
        return report

    report["row_count"] = int(len(data))
    missing = [column for column in STANDARD_COLUMNS if column not in data.columns]
    if missing:
        report["is_valid"] = False
        report["errors"].append(f"Missing columns: {missing}")
        return report

    frame = data[STANDARD_COLUMNS].copy()
    dates = pd.to_datetime(frame["date"], errors="coerce")
    if dates.isna().any():
        report["is_valid"] = False
        report["errors"].append("Date column contains invalid values.")
    else:
        report["start_date"] = dates.min().date().isoformat()
        report["end_date"] = dates.max().date().isoformat()
        if not dates.is_monotonic_increasing:
            report["is_valid"] = False
            report["errors"].append("Date column is not increasing.")

    numeric_columns = ["open", "high", "low", "close", "volume"]
    numeric = frame[numeric_columns].apply(pd.to_numeric, errors="coerce")
    if numeric[["open", "high", "low", "close"]].isna().any().any():
        report["is_valid"] = False
        report["errors"].append("Price columns contain missing or invalid values.")
    if numeric["volume"].isna().any():
        report["is_valid"] = False
        report["errors"].append("Volume column contains missing or invalid values.")
    if numeric["close"].isna().any():
        report["is_valid"] = False
        report["errors"].append("Close column contains missing values.")

    if (numeric[["open", "high", "low", "close"]] <= 0).any().any():
        report["is_valid"] = False
        report["errors"].append("OHLC price columns must be positive.")
    if (numeric["volume"] < 0).any():
        report["is_valid"] = False
        report["errors"].append("Volume must be non-negative.")
    if not (numeric["high"] >= numeric[["open", "close", "low"]].max(axis=1)).all():
        report["is_valid"] = False
        report["errors"].append("High must be greater than or equal to open, close, and low.")
    if not (numeric["low"] <= numeric[["open", "close", "high"]].min(axis=1)).all():
        report["is_valid"] = False
        report["errors"].append("Low must be less than or equal to open, close, and high.")

    if len(frame) < min_rows:
        report["warnings"].append(f"Row count is below {min_rows}.")

    if not numeric["close"].dropna().empty:
        report["latest_close"] = float(numeric["close"].dropna().iloc[-1])
    return report


def check_data_freshness(data: pd.DataFrame, max_age_days: int = 7) -> dict:
    """Check whether the latest date is older than the allowed age."""
    if data is None or data.empty or "date" not in data.columns:
        raise ValueError("Data must contain a non-empty date column.")

    dates = pd.to_datetime(data["date"], errors="coerce")
    if dates.isna().all():
        raise ValueError("Date column contains no valid dates.")

    latest_date = dates.max().normalize()
    today = pd.Timestamp.today().normalize()
    age_days = int((today - latest_date).days)
    is_fresh = age_days <= max_age_days
    return {
        "is_fresh": bool(is_fresh),
        "latest_date": latest_date.date().isoformat(),
        "age_days": age_days,
        "max_age_days": int(max_age_days),
        "warning": None if is_fresh else f"Latest data is {age_days} days old.",
    }


def build_data_quality_report(market: str, symbol: str, data: pd.DataFrame, max_age_days: int = 7) -> dict:
    quality = validate_ohlcv_data(data)
    try:
        freshness = check_data_freshness(data, max_age_days=max_age_days)
    except ValueError as error:
        freshness = {"is_fresh": False, "warning": str(error)}

    warnings = list(quality["warnings"])
    if freshness.get("warning"):
        warnings.append(str(freshness["warning"]))

    is_valid = bool(quality["is_valid"] and not quality["errors"])
    return {
        "market": str(market).strip().lower(),
        "symbol": str(symbol).strip().upper(),
        "is_valid": is_valid,
        "status": "valid" if is_valid and not warnings else ("error" if quality["errors"] else "warning"),
        "warnings": warnings,
        "errors": quality["errors"],
        "row_count": quality["row_count"],
        "start_date": quality["start_date"],
        "end_date": quality["end_date"],
        "latest_close": quality["latest_close"],
        "freshness": freshness,
    }
