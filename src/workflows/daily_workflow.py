from __future__ import annotations

from datetime import datetime
from pathlib import Path
from time import perf_counter

import pandas as pd

from src.data.watchlist_manager import normalize_symbols
from src.reports.daily_research_report import (
    DEFAULT_DAILY_REPORT_DIR,
    build_daily_research_report,
    save_daily_research_report,
)
from src.strategies.trend_score import latest_trend_score
from src.workflows.run_log import generate_run_id


def _data_source_label(data: pd.DataFrame) -> str:
    if data.attrs.get("is_sample_data"):
        return "sample"
    return str(data.attrs.get("data_source", "real"))


def _trend_summary(trend_scores: pd.DataFrame) -> dict:
    if trend_scores.empty:
        average_score = 0.0
    else:
        average_score = float(pd.to_numeric(trend_scores["score"], errors="coerce").dropna().mean())
        if pd.isna(average_score):
            average_score = 0.0
    return {
        "strong_trend_count": int((trend_scores["status"] == "Strong trend").sum()) if not trend_scores.empty else 0,
        "watchlist_count": int((trend_scores["status"] == "Watchlist").sum()) if not trend_scores.empty else 0,
        "neutral_count": int((trend_scores["status"] == "Neutral").sum()) if not trend_scores.empty else 0,
        "weak_count": int((trend_scores["status"] == "Weak").sum()) if not trend_scores.empty else 0,
        "average_score": average_score,
    }


def run_daily_research_workflow(
    market: str,
    watchlist_name: str,
    symbols: list[str],
    fetch_data_func,
    output_dir: str | Path | None = None,
) -> dict:
    """Run the local daily research workflow once and save a daily report."""
    run_id = generate_run_id()
    started_at = datetime.now()
    start_time = perf_counter()
    market_code = market.strip().lower()
    if market_code not in {"us", "cn"}:
        raise ValueError("market must be 'us' or 'cn'.")

    clean_symbols = normalize_symbols(symbols)
    if not clean_symbols:
        raise ValueError("symbols cannot be empty.")

    rows = []
    success_symbols = []
    failed_symbols = []
    data_sources = []
    data_source_by_symbol = {}
    warnings = []

    for symbol in clean_symbols:
        try:
            data = fetch_data_func(market_code, symbol)
            data_source = _data_source_label(data)
            score = latest_trend_score(symbol, data)
            rows.append(
                {
                    "symbol": score.symbol,
                    "score": score.score,
                    "status": score.status,
                    "close": score.close,
                    "rsi14": score.rsi14,
                    "data_source": data_source,
                }
            )
            success_symbols.append(symbol)
            data_sources.append(data_source)
            data_source_by_symbol[symbol] = data_source
            if data_source == "sample":
                warnings.append(f"{symbol} used local sample fallback data.")
        except Exception as error:
            failed_symbols.append({"symbol": symbol, "error": str(error)})

    trend_scores = pd.DataFrame(rows, columns=["symbol", "score", "status", "close", "rsi14", "data_source"])
    summary = _trend_summary(trend_scores)

    if trend_scores.empty:
        finished_at = datetime.now()
        elapsed_seconds = perf_counter() - start_time
        return {
            "run_id": run_id,
            "started_at": started_at.isoformat(timespec="seconds"),
            "finished_at": finished_at.isoformat(timespec="seconds"),
            "created_at": finished_at.isoformat(timespec="seconds"),
            "elapsed_seconds": elapsed_seconds,
            "success": False,
            "market": market_code,
            "watchlist_name": str(watchlist_name),
            "total_symbols": len(clean_symbols),
            "success_count": len(success_symbols),
            "failed_count": len(failed_symbols),
            "success_symbols": success_symbols,
            "failed_symbols": failed_symbols,
            "report_id": None,
            "report_path": None,
            "trend_scores": trend_scores,
            "summary": summary,
            "data_sources": data_source_by_symbol,
            "warnings": warnings,
            "error_message": "No symbols were processed successfully. Daily report was not saved.",
            "error": "No symbols were processed successfully. Daily report was not saved.",
        }

    data_source_summary = {source: data_sources.count(source) for source in sorted(set(data_sources))}
    report = build_daily_research_report(
        market=market_code,
        watchlist_name=str(watchlist_name),
        trend_scores=trend_scores,
        data_source_summary=data_source_summary,
    )
    if output_dir is None:
        saved_report = save_daily_research_report(report)
        report_dir = DEFAULT_DAILY_REPORT_DIR
    else:
        saved_report = save_daily_research_report(report, output_dir)
        report_dir = Path(output_dir)
    report_path = (report_dir / f"{saved_report['report_id']}.json").resolve()
    finished_at = datetime.now()
    elapsed_seconds = perf_counter() - start_time

    return {
        "run_id": run_id,
        "started_at": started_at.isoformat(timespec="seconds"),
        "finished_at": finished_at.isoformat(timespec="seconds"),
        "created_at": finished_at.isoformat(timespec="seconds"),
        "elapsed_seconds": elapsed_seconds,
        "success": True,
        "market": market_code,
        "watchlist_name": str(watchlist_name),
        "total_symbols": len(clean_symbols),
        "success_count": len(success_symbols),
        "failed_count": len(failed_symbols),
        "success_symbols": success_symbols,
        "failed_symbols": failed_symbols,
        "report_id": saved_report["report_id"],
        "report_path": str(report_path),
        "report": saved_report,
        "trend_scores": trend_scores.sort_values("score", ascending=False).reset_index(drop=True),
        "summary": summary,
        "data_sources": data_source_by_symbol,
        "warnings": warnings,
    }
