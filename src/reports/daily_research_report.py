from __future__ import annotations

import json
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


DEFAULT_DAILY_REPORT_DIR = Path(__file__).resolve().parents[2] / "reports" / "daily"
REPORT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
SENSITIVE_KEYS = {"api_key", "apikey", "secret", "password", "token"}
DISCLAIMER = "本报告仅用于学习、研究和模拟交易演示，不构成投资建议。"
SUMMARY_COLUMNS = [
    "report_id",
    "created_at",
    "market",
    "watchlist_name",
    "total_symbols",
    "strong_trend_count",
    "average_score",
]


def _ensure_report_dir(output_dir: str | Path = DEFAULT_DAILY_REPORT_DIR) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _validate_safe_name(value: str, field_name: str) -> str:
    if not value or not REPORT_ID_PATTERN.fullmatch(value):
        raise ValueError(f"{field_name} may only contain letters, numbers, underscores, and hyphens.")
    if ".." in value or "/" in value or "\\" in value:
        raise ValueError(f"{field_name} contains unsafe path characters.")
    return value


def _report_path(report_id: str, output_dir: str | Path = DEFAULT_DAILY_REPORT_DIR) -> Path:
    safe_report_id = _validate_safe_name(report_id, "report_id")
    base_dir = _ensure_report_dir(output_dir)
    path = (base_dir / f"{safe_report_id}.json").resolve()
    if path.parent != base_dir:
        raise ValueError("Daily report path must stay inside the daily report directory.")
    return path


def _has_sensitive_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_").replace(" ", "_")
            if normalized in SENSITIVE_KEYS or normalized.endswith("_secret") or normalized.endswith("_token"):
                return True
            if _has_sensitive_key(item):
                return True
    elif isinstance(value, list):
        return any(_has_sensitive_key(item) for item in value)
    return False


def _json_safe(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        return value.item()
    if pd.isna(value):
        return None
    return value


def _normalize_trend_scores(trend_scores: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "股票代码": "symbol",
        "趋势分数": "score",
        "状态": "status",
        "收盘价": "close",
        "RSI14": "rsi14",
        "数据来源": "data_source",
    }
    data = trend_scores.rename(columns=rename_map).copy()
    required = ["symbol", "score", "status", "close", "rsi14"]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError(f"trend_scores missing columns: {missing}")
    data["score"] = pd.to_numeric(data["score"], errors="coerce")
    data["close"] = pd.to_numeric(data["close"], errors="coerce")
    data["rsi14"] = pd.to_numeric(data["rsi14"], errors="coerce")
    data = data.dropna(subset=["symbol"]).copy()
    data["symbol"] = data["symbol"].astype(str)
    return data


def _symbol_records(data: pd.DataFrame) -> list[dict]:
    columns = ["symbol", "score", "status", "close", "rsi14"]
    existing_columns = [column for column in columns if column in data.columns]
    return [_json_safe(record) for record in data[existing_columns].to_dict(orient="records")]


def generate_daily_report_id(prefix: str = "daily_report") -> str:
    """Generate a path-safe daily report id."""
    safe_prefix = _validate_safe_name(prefix, "prefix")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = secrets.token_hex(4)
    return f"{safe_prefix}_{timestamp}_{suffix}"


def build_daily_research_report(
    market: str,
    watchlist_name: str,
    trend_scores: pd.DataFrame,
    data_source_summary: dict | None = None,
    paper_portfolio_summary: dict | None = None,
    recent_backtest_summary: dict | None = None,
) -> dict:
    """Build one local daily research report from already calculated data."""
    data = _normalize_trend_scores(trend_scores)
    notes = []
    if data.empty:
        notes.append("No trend score rows were available when this report was generated.")

    strong_count = int((data["status"] == "Strong trend").sum())
    watchlist_count = int((data["status"] == "Watchlist").sum())
    neutral_count = int((data["status"] == "Neutral").sum())
    weak_count = int(((data["status"] == "Weak") | (data["score"] < 40)).sum())
    average_score = float(data["score"].dropna().mean()) if not data["score"].dropna().empty else 0.0

    ranked = data.sort_values("score", ascending=False, na_position="last")
    risk_rows = data[(data["status"] == "Weak") | (data["score"] < 40)].sort_values(
        "score",
        ascending=True,
        na_position="last",
    )

    report = {
        "report_id": generate_daily_report_id(),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "market": str(market),
        "watchlist_name": str(watchlist_name),
        "disclaimer": DISCLAIMER,
        "market_summary": {
            "total_symbols": int(len(data)),
            "strong_trend_count": strong_count,
            "watchlist_count": watchlist_count,
            "neutral_count": neutral_count,
            "weak_count": weak_count,
            "average_score": average_score,
        },
        "top_symbols": _symbol_records(ranked.head(5)),
        "risk_symbols": _symbol_records(risk_rows.head(10)),
        "data_source_summary": _json_safe(data_source_summary or {}),
        "paper_portfolio_summary": _json_safe(paper_portfolio_summary or {}),
        "recent_backtest_summary": _json_safe(recent_backtest_summary or {}),
        "notes": notes,
    }
    if _has_sensitive_key(report):
        raise ValueError("Daily reports must not contain API keys, secrets, passwords, or tokens.")
    return report


def save_daily_research_report(
    report: dict,
    output_dir: str | Path = DEFAULT_DAILY_REPORT_DIR,
) -> dict:
    """Save one daily research report as local JSON."""
    clean_report = _json_safe(report)
    if _has_sensitive_key(clean_report):
        raise ValueError("Daily reports must not contain API keys, secrets, passwords, or tokens.")
    report_id = _validate_safe_name(str(clean_report.get("report_id", "")), "report_id")
    path = _report_path(report_id, output_dir)
    path.write_text(json.dumps(clean_report, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return clean_report


def load_daily_research_report(
    report_id: str,
    output_dir: str | Path = DEFAULT_DAILY_REPORT_DIR,
) -> dict:
    """Load one daily research report by id."""
    path = _report_path(report_id, output_dir)
    if not path.exists():
        raise FileNotFoundError(f"Daily research report not found: {report_id}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Daily research report JSON is invalid: {report_id}") from error


def list_daily_research_reports(
    output_dir: str | Path = DEFAULT_DAILY_REPORT_DIR,
) -> pd.DataFrame:
    """List saved daily reports as a compact summary table."""
    base_dir = _ensure_report_dir(output_dir)
    rows = []
    for path in sorted(base_dir.glob("*.json"), reverse=True):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        summary = report.get("market_summary", {})
        rows.append(
            {
                "report_id": report.get("report_id", path.stem),
                "created_at": report.get("created_at"),
                "market": report.get("market"),
                "watchlist_name": report.get("watchlist_name"),
                "total_symbols": summary.get("total_symbols"),
                "strong_trend_count": summary.get("strong_trend_count"),
                "average_score": summary.get("average_score"),
            }
        )
    return pd.DataFrame(rows, columns=SUMMARY_COLUMNS)


def delete_daily_research_report(
    report_id: str,
    output_dir: str | Path = DEFAULT_DAILY_REPORT_DIR,
) -> None:
    """Delete one daily report inside the daily report directory."""
    path = _report_path(report_id, output_dir)
    if not path.exists():
        raise FileNotFoundError(f"Daily research report not found: {report_id}")
    path.unlink()


def daily_report_to_markdown(report: dict) -> str:
    """Convert a daily research report to readable Markdown."""
    summary = report.get("market_summary", {})
    lines = [
        "# 每日量化研究报告",
        "",
        f"- 生成时间：{report.get('created_at', '')}",
        f"- 市场：{report.get('market', '')}",
        f"- Watchlist：{report.get('watchlist_name', '')}",
        f"- 免责声明：{report.get('disclaimer', DISCLAIMER)}",
        "",
        "## 市场摘要",
        "",
        f"- 股票数量：{summary.get('total_symbols', 0)}",
        f"- Strong trend：{summary.get('strong_trend_count', 0)}",
        f"- Watchlist：{summary.get('watchlist_count', 0)}",
        f"- Neutral：{summary.get('neutral_count', 0)}",
        f"- Weak：{summary.get('weak_count', 0)}",
        f"- 平均趋势分数：{summary.get('average_score', 0):.2f}",
        "",
        "## Top 趋势股票",
        "",
    ]
    top_symbols = report.get("top_symbols", [])
    if top_symbols:
        for item in top_symbols:
            lines.append(
                f"- {item.get('symbol')}: score={item.get('score')}, status={item.get('status')}, "
                f"close={item.get('close')}, rsi14={item.get('rsi14')}"
            )
    else:
        lines.append("- 暂无 Top 趋势股票。")

    lines.extend(["", "## 风险观察股票", ""])
    risk_symbols = report.get("risk_symbols", [])
    if risk_symbols:
        for item in risk_symbols:
            lines.append(
                f"- {item.get('symbol')}: score={item.get('score')}, status={item.get('status')}, "
                f"close={item.get('close')}, rsi14={item.get('rsi14')}"
            )
    else:
        lines.append("- 暂无 Weak 或低分股票。")

    sections = [
        ("数据源状态", report.get("data_source_summary", {})),
        ("模拟账户摘要", report.get("paper_portfolio_summary", {})),
        ("最近回测摘要", report.get("recent_backtest_summary", {})),
    ]
    for title, value in sections:
        lines.extend(["", f"## {title}", "", "```json", json.dumps(value, ensure_ascii=False, indent=2), "```"])

    notes = report.get("notes", [])
    lines.extend(["", "## 风险提示", ""])
    lines.append("- 本报告仅用于学习、研究和模拟交易演示，不构成投资建议。")
    lines.append("- 历史数据和模型评分不代表未来收益。")
    lines.append("- 当前系统不连接真实券商，不自动下单。")
    for note in notes:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def export_daily_report_summary_csv(
    output_dir: str | Path = DEFAULT_DAILY_REPORT_DIR,
) -> str:
    """Export daily report summaries as a CSV string."""
    reports = list_daily_research_reports(output_dir)
    return reports.to_csv(index=False)
