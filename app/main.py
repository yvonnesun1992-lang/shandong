from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.backtest.portfolio_backtest import run_portfolio_backtest
from src.backtest.simple_backtest import run_simple_backtest
from src.config.settings import load_settings, reset_settings, save_settings
from src.data.cn_data import get_cn_ohlcv
from src.data.data_quality import build_data_quality_report
from src.data.price_cache import delete_cached_price_data, list_cached_symbols
from src.data.us_data import get_us_ohlcv
from src.data.watchlist_manager import load_watchlists, normalize_symbols, save_watchlist, validate_watchlist_name
from src.paper_trading.portfolio import (
    buy_paper_position,
    calculate_portfolio_summary,
    get_trade_history,
    load_paper_portfolio,
    reset_paper_portfolio,
    sell_paper_position,
)
from src.portfolio.allocation import build_allocation_plan
from src.reports.backtest_report import (
    delete_backtest_report,
    export_report_summary_csv,
    list_backtest_reports,
    load_backtest_report,
    save_backtest_report,
)
from src.reports.daily_research_report import (
    build_daily_research_report,
    daily_report_to_markdown,
    delete_daily_research_report,
    export_daily_report_summary_csv,
    list_daily_research_reports,
    load_daily_research_report,
    save_daily_research_report,
)
from src.strategies.trend_score import CN_WATCHLIST, US_WATCHLIST, add_trend_scores, latest_trend_score
from src.strategies.presets import (
    DEFAULT_PRESET_NAMES,
    delete_strategy_preset,
    load_strategy_presets,
    save_strategy_preset,
)
from src.strategies.comparison import compare_strategy_presets
from src.system.health_check import health_check_to_dataframe, run_system_health_check
from src.ui.layout import (
    dataframe_to_csv_bytes,
    format_data_source_label,
    format_health_status,
    format_return_pct,
    render_compact_table,
    render_empty_state,
    render_metric_row,
    render_parameter_summary,
    render_page_header,
    render_risk_disclaimer,
    render_section_header,
    render_status_message,
)
from src.ui.home import build_home_summary
from src.workflows.daily_workflow import run_daily_research_workflow
from src.workflows.run_log import (
    delete_workflow_run_log,
    export_workflow_run_summary_csv,
    list_workflow_run_logs,
    load_workflow_run_log,
    save_workflow_run_log,
)


st.set_page_config(page_title="Shandong Quant Research", layout="wide")


SAMPLE_WARNING = "当前真实数据源获取失败，正在使用本地示例数据。示例数据仅用于功能演示，不代表真实行情，不构成投资建议。"
DISCLAIMER = "本系统仅用于学习、研究、历史回测和模拟交易演示，不构成投资建议。历史回测不代表未来收益。当前版本不连接真实券商，不自动下单。"
CACHE_NOTE = "行情数据使用缓存，默认缓存 1 小时。如需强制刷新，请重启应用或清理 Streamlit cache。"
PAPER_TRADING_WARNING = "模拟交易仅用于学习和功能演示，不代表真实交易，不构成投资建议，不会连接真实券商，也不会产生真实订单。"
PORTFOLIO_BACKTEST_WARNING = "组合回测仅用于历史研究和功能演示，不代表未来收益，不构成投资建议。"
STRATEGY_COMPARISON_WARNING = "策略对比仅用于历史研究和功能演示。历史回测不代表未来收益，不构成投资建议。"
ALLOCATION_LAB_WARNING = "组合配置实验室仅供投资研究，不构成投资建议，不代表未来收益，不会生成真实交易指令。"
REPORT_CENTER_WARNING = "历史回测报告仅用于研究和复盘，不代表未来收益，不构成投资建议。"
DAILY_REPORT_WARNING = "本报告仅用于学习、研究和模拟交易演示，不构成投资建议。历史数据和模型评分不代表未来收益。"
DAILY_WORKFLOW_WARNING = "每日流程仅用于学习、研究和模拟交易演示，不构成投资建议。数据源可能失败或延迟，历史评分不代表未来收益。"
WORKFLOW_RUN_LOG_WARNING = "运行记录仅用于本地研究流程审计和复盘，不代表投资建议，不会产生真实交易。"
PRICE_CACHE_WARNING = "行情缓存仅用于研究和演示，不代表实时行情，不构成投资建议。"
SETTINGS_WARNING = "系统设置仅用于本地研究环境配置，不应保存任何真实账户、密码、API key 或券商凭证。"
SYSTEM_HEALTH_WARNING = "系统健康检查仅用于本地研究环境诊断，不代表投资建议，不会连接真实券商，也不会产生真实订单。"

# V1.18 raw refresh marker: keep app/main.py as real multiline Python.
# V1.18 formatting verification marker 6: remote raw must stay multiline.


@st.cache_data(show_spinner=False, ttl=3600)
def load_data(market: str, symbol: str, use_cache: bool = True) -> pd.DataFrame:
    if market == "美股":
        return get_us_ohlcv(symbol, use_cache=use_cache)
    return get_cn_ohlcv(symbol, use_cache=use_cache)


def fetch_price_data(market: str, symbol: str, refresh_cache: bool = False, use_cache: bool = True) -> pd.DataFrame:
    if market == "美股":
        return get_us_ohlcv(symbol, refresh_cache=refresh_cache, use_cache=use_cache)
    return get_cn_ohlcv(symbol, refresh_cache=refresh_cache, use_cache=use_cache)


def market_label_from_setting(default_market: str) -> str:
    if str(default_market).strip().lower() == "cn":
        return "A股"
    return "美股"


def is_sample_data(data: pd.DataFrame) -> bool:
    return bool(data.attrs.get("is_sample_data", False))


def data_source_label(data: pd.DataFrame) -> str:
    if is_sample_data(data):
        return format_data_source_label("sample")
    source = str(data.attrs.get("data_source", "remote"))
    return format_data_source_label(source)


def show_data_source_status(data: pd.DataFrame) -> None:
    if is_sample_data(data):
        st.warning(SAMPLE_WARNING)
    elif data.attrs.get("data_source") == "cache":
        st.info("数据源：本地行情缓存")
    else:
        st.info("数据源：实时/历史行情数据")


def trend_scores_to_csv(rank_table: pd.DataFrame) -> bytes:
    export = rank_table.rename(
        columns={
            "股票代码": "symbol",
            "趋势分数": "score",
            "状态": "status",
            "收盘价": "close",
            "RSI14": "rsi14",
            "数据来源": "data_source",
        }
    )
    return export.to_csv(index=False).encode("utf-8-sig")


def trades_to_csv(trades: list[dict]) -> bytes:
    return pd.DataFrame(trades).to_csv(index=False).encode("utf-8-sig")


def dataframe_to_csv(data: pd.DataFrame) -> bytes:
    return dataframe_to_csv_bytes(data)


def report_to_json_bytes(report: dict) -> bytes:
    return json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")


def report_records_to_csv(records: list[dict]) -> bytes:
    return pd.DataFrame(records).to_csv(index=False).encode("utf-8-sig")


def strategy_comparison_to_json_bytes(comparison_result: dict) -> bytes:
    # Export the local research comparison result without changing backtest logic.
    # This stays a dashboard-only serialization helper and never places orders.
    # V1.17 raw refresh marker: keep this helper as real multiline Python.
    export = {
        "ranking": comparison_result.get("ranking", pd.DataFrame()).to_dict(orient="records"),
        "failed_presets": comparison_result.get("failed_presets", []),
        "results": {},
    }
    for preset_name, result in comparison_result.get("results", {}).items():
        export["results"][preset_name] = {
            "summary": result.get("summary", {}),
            "equity_curve": result.get("equity_curve", pd.DataFrame()).to_dict(orient="records"),
            "trades": result.get("trades", pd.DataFrame()).to_dict(orient="records"),
        }
    return json.dumps(export, ensure_ascii=False, indent=2, default=str).encode("utf-8")


def allocation_summary_to_json_bytes(allocation_result: dict) -> bytes:
    export = {
        "summary": allocation_result.get("summary", {}),
        "warnings": allocation_result.get("warnings", []),
        "failed_symbols": allocation_result.get("failed_symbols", []),
        "disclaimer": "仅供投资研究，不构成投资建议，不代表未来收益。",
    }
    return json.dumps(export, ensure_ascii=False, indent=2, default=str).encode("utf-8")


def text_to_download(text: str) -> bytes:
    return text.encode("utf-8-sig")


def parse_symbols_text(symbols_text: str) -> list[str]:
    raw_symbols = symbols_text.replace("，", ",").replace("\n", ",").split(",")
    return normalize_symbols(raw_symbols)


def parse_current_positions_text(positions_text: str) -> tuple[dict[str, float], list[str]]:
    positions: dict[str, float] = {}
    warnings = []
    for line in positions_text.replace("，", ",").splitlines():
        clean_line = line.strip()
        if not clean_line:
            continue
        parts = [part.strip() for part in clean_line.split(",")]
        if len(parts) != 2 or not parts[0]:
            warnings.append(f"当前持仓格式错误，已忽略：{clean_line}")
            continue
        try:
            quantity = float(parts[1])
        except ValueError:
            warnings.append(f"当前持仓数量无效，已忽略：{clean_line}")
            continue
        if quantity < 0:
            warnings.append(f"当前持仓数量不能为负，已忽略：{clean_line}")
            continue
        positions[parts[0].upper()] = quantity
    return positions, warnings


def default_watchlist_name(market: str) -> str:
    if market == "美股":
        return "us_default"
    return "cn_default"


def default_market_symbols(market: str) -> list[str]:
    if market == "美股":
        return US_WATCHLIST.copy()
    return CN_WATCHLIST.copy()


def build_rank_table(market: str, symbols: list[str], use_cache: bool = True) -> pd.DataFrame:
    rows = []
    for symbol in symbols:
        try:
            data = load_data(market, symbol, use_cache=use_cache)
            score = latest_trend_score(symbol, data)
            rows.append(
                {
                    "股票代码": score.symbol,
                    "趋势分数": score.score,
                    "状态": score.status,
                    "收盘价": round(score.close, 2),
                    "RSI14": round(score.rsi14, 2),
                    "数据来源": data_source_label(data),
                }
            )
        except Exception as error:
            rows.append(
                {
                    "股票代码": symbol,
                    "趋势分数": None,
                    "状态": f"数据错误: {error}",
                    "收盘价": None,
                    "RSI14": None,
                    "数据来源": "不可用",
                }
            )
    return pd.DataFrame(rows).sort_values("趋势分数", ascending=False, na_position="last")


def load_price_data_for_symbols(
    market: str,
    symbols: list[str],
    use_cache: bool = True,
) -> tuple[dict[str, pd.DataFrame], list[str]]:
    price_data = {}
    failed_symbols = []
    for symbol in symbols:
        try:
            price_data[symbol] = load_data(market, symbol, use_cache=use_cache)
        except Exception:
            failed_symbols.append(symbol)
    return price_data, failed_symbols


def build_allocation_inputs(
    market: str,
    symbols: list[str],
    use_cache: bool = True,
) -> tuple[dict[str, float], dict[str, float], list[str], bool]:
    scores = {}
    prices = {}
    failed_symbols = []
    used_sample_data = False
    price_data, load_failures = load_price_data_for_symbols(market, symbols, use_cache=use_cache)
    failed_symbols.extend(load_failures)
    for symbol, data in price_data.items():
        try:
            score = latest_trend_score(symbol, data)
            scores[symbol] = float(score.score)
            prices[symbol] = float(score.close)
            used_sample_data = used_sample_data or is_sample_data(data)
        except Exception:
            failed_symbols.append(symbol)
    return scores, prices, sorted(set(failed_symbols)), used_sample_data


def data_source_summary_from_rank_table(rank_table: pd.DataFrame) -> dict:
    if rank_table.empty or "数据来源" not in rank_table.columns:
        return {}
    counts = rank_table["数据来源"].fillna("未知").value_counts().to_dict()
    return {str(key): int(value) for key, value in counts.items()}


def strategy_presets_to_dataframe(presets: dict) -> pd.DataFrame:
    rows = []
    for name, preset in presets.items():
        rows.append(
            {
                "name": name,
                "description": preset.get("description", ""),
                "min_score_to_buy": preset.get("min_score_to_buy"),
                "min_score_to_hold": preset.get("min_score_to_hold"),
                "max_position_pct": preset.get("max_position_pct"),
                "rebalance_frequency": preset.get("rebalance_frequency"),
            }
        )
    return pd.DataFrame(rows)


def latest_backtest_summary() -> dict:
    reports = list_backtest_reports()
    if reports.empty:
        return {}
    latest_report_id = str(reports.iloc[0]["report_id"])
    report = load_backtest_report(latest_report_id)
    return {
        "report_id": latest_report_id,
        "report_type": report.get("report_type"),
        "created_at": report.get("created_at"),
        "summary": report.get("summary", {}),
    }


def market_label_from_code(market: str) -> str:
    if market.lower() == "cn":
        return "A股"
    return "美股"


def market_code_from_label(market: str) -> str:
    if market == "A股":
        return "cn"
    return "us"


def fetch_workflow_data(market: str, symbol: str) -> pd.DataFrame:
    return load_data(market_label_from_code(market), symbol)


def latest_prices_for_positions(portfolio: dict) -> dict[str, float]:
    prices = {}
    for symbol, position in portfolio.get("positions", {}).items():
        try:
            market_label = market_label_from_code(position.get("market", "us"))
            data = load_data(market_label, symbol)
            prices[symbol] = float(data.iloc[-1]["close"])
        except Exception:
            prices[symbol] = float(position.get("avg_cost", 0.0))
    return prices


def latest_reports_overview(max_rows: int = 3) -> pd.DataFrame:
    tables = []
    try:
        daily_reports = list_daily_research_reports()
        if not daily_reports.empty:
            daily = daily_reports.copy()
            daily["report_type"] = "daily_research"
            tables.append(daily)
    except Exception:
        pass
    try:
        backtest_reports = list_backtest_reports()
        if not backtest_reports.empty:
            tables.append(backtest_reports.copy())
    except Exception:
        pass
    if not tables:
        return pd.DataFrame()
    reports = pd.concat(tables, ignore_index=True, sort=False)
    if "created_at" in reports.columns:
        reports = reports.sort_values("created_at", ascending=False, na_position="last")
    return reports.head(max_rows)


def show_score_rules() -> None:
    with st.expander("趋势评分规则说明", expanded=False):
        st.markdown(
            """
- 价格高于 MA20：+15
- 价格高于 MA60：+20
- 价格高于 MA120：+20
- MA20 高于 MA60：+15
- MA60 高于 MA120：+15
- RSI 在 50 到 75：+10
- 成交量高于成交量 MA20：+5

分数解释：

- 80-100：Strong trend
- 60-79：Watchlist
- 40-59：Neutral
- 40 以下：Weak
"""
        )


def main() -> None:
    render_page_header(
        "Shandong Quant Research",
        "A-share & US stock quant research prototype",
    )
    try:
        settings = load_settings()
        settings_error = None
    except Exception as error:
        settings = {
            "cache": {"enabled": True, "max_age_days": 7},
            "paper_trading": {"initial_cash": 100000.0},
            "dashboard": {"default_market": "us", "show_disclaimer": True},
            "workflow": {"min_success_symbols": 1},
            "reports": {},
        }
        settings_error = error
        st.error(f"无法读取系统设置，已使用本次运行的默认值：{error}")

    if settings.get("dashboard", {}).get("show_disclaimer", True):
        render_risk_disclaimer()
    cache_enabled = bool(settings.get("cache", {}).get("enabled", True))

    default_market_label = market_label_from_setting(settings.get("dashboard", {}).get("default_market", "us"))
    default_market_index = ["美股", "A股"].index(default_market_label)
    st.sidebar.header("研究配置")
    market = st.sidebar.radio("市场", ["美股", "A股"], index=default_market_index)
    fallback_symbols = default_market_symbols(market)
    fallback_watchlist_name = default_watchlist_name(market)

    st.sidebar.subheader("自选股管理")
    try:
        watchlists = load_watchlists()
    except Exception as error:
        st.sidebar.error(f"无法读取自选股配置：{error}")
        watchlists = {fallback_watchlist_name: fallback_symbols}

    watchlist_names = sorted(watchlists)
    if fallback_watchlist_name in watchlist_names:
        default_index = watchlist_names.index(fallback_watchlist_name)
    else:
        default_index = 0

    selected_watchlist = st.sidebar.selectbox("选择 watchlist", watchlist_names, index=default_index)
    st.sidebar.metric("当前股票数量", len(watchlists.get(selected_watchlist, fallback_symbols)))
    new_watchlist_name = st.sidebar.text_input("新 watchlist 名称（可选）", value="")
    current_symbols = watchlists.get(selected_watchlist, fallback_symbols)
    symbols_text = st.sidebar.text_area(
        "股票池（每行一个，或用逗号分隔）",
        value="\n".join(current_symbols),
        height=220,
        key=f"symbols_text_{market}_{selected_watchlist}",
    )

    symbols = parse_symbols_text(symbols_text)
    if st.sidebar.button("保存自选股"):
        target_name = new_watchlist_name.strip() or selected_watchlist
        try:
            validate_watchlist_name(target_name)
            save_watchlist(target_name, symbols)
            st.sidebar.success(f"已保存自选股：{target_name}")
        except Exception as error:
            st.sidebar.error(f"保存失败：{error}")

    st.sidebar.caption(CACHE_NOTE)
    st.sidebar.caption("系统健康页可检查本地配置、缓存、报告和运行环境。")

    if not symbols:
        st.warning("股票池为空，请在左侧输入至少一个股票代码。")
        st.stop()

    (
        home_tab,
        rank_tab,
        strategy_lab_tab,
        strategy_comparison_tab,
        allocation_lab_tab,
        chart_tab,
        backtest_tab,
        portfolio_tab,
        paper_tab,
        workflow_tab,
        daily_tab,
        report_tab,
        data_quality_tab,
        run_log_tab,
        settings_tab,
        system_health_tab,
        info_tab,
    ) = st.tabs(
        [
            "首页",
            "市场总览",
            "策略实验室",
            "策略对比",
            "组合配置实验室",
            "单股分析",
            "单股回测",
            "组合回测",
            "模拟交易",
            "每日流程",
            "每日研究报告",
            "报告中心",
            "数据质量",
            "运行记录",
            "系统设置",
            "系统健康",
            "说明",
        ]
    )

    with home_tab:
        render_section_header(
            "首页",
            "快速查看系统状态、趋势概览、模拟账户、最近 workflow 和报告。",
        )
        st.caption("本系统用于学习、研究、历史回测和模拟交易演示，不构成投资建议。")

        try:
            home_rank_table = build_rank_table(market, symbols, use_cache=cache_enabled)
        except Exception as error:
            home_rank_table = pd.DataFrame()
            st.warning(f"趋势评分暂不可用：{error}")

        try:
            home_portfolio = load_paper_portfolio()
            home_latest_prices = latest_prices_for_positions(home_portfolio)
            home_paper_summary = calculate_portfolio_summary(home_portfolio, home_latest_prices)
        except Exception as error:
            home_paper_summary = {}
            st.info(f"模拟账户摘要暂不可用：{error}")

        try:
            home_health_summary = run_system_health_check()
        except Exception as error:
            home_health_summary = {"overall_status": "unknown", "note": str(error)}
            st.info(f"系统健康摘要暂不可用：{error}")

        try:
            home_workflow_runs = list_workflow_run_logs()
        except Exception as error:
            home_workflow_runs = pd.DataFrame()
            st.info(f"workflow 运行记录暂不可用：{error}")

        home_reports = latest_reports_overview()
        home_summary = build_home_summary(
            market=market,
            watchlist_name=selected_watchlist,
            symbols=symbols,
            trend_scores=home_rank_table,
            paper_portfolio_summary=home_paper_summary,
            health_summary=home_health_summary,
            latest_workflow_runs=home_workflow_runs,
            latest_reports=home_reports,
        )

        render_metric_row(
            [
                {"label": "当前市场", "value": home_summary["market"]},
                {"label": "当前 watchlist", "value": home_summary["watchlist_name"]},
                {"label": "股票数量", "value": home_summary["symbol_count"]},
                {"label": "系统健康", "value": format_health_status(home_summary["health_status"])},
            ]
        )
        render_metric_row(
            [
                {"label": "Strong trend", "value": home_summary["strong_trend_count"]},
                {"label": "Watchlist", "value": home_summary["watchlist_count"]},
                {"label": "Weak", "value": home_summary["weak_count"]},
                {"label": "模拟总资产", "value": f"{home_summary['paper_total_value']:,.2f}"},
            ]
        )

        overview_col, account_col = st.columns(2)
        with overview_col:
            render_section_header("今日研究概览", "当前自选股的趋势分布和重点观察对象。")
            st.metric("平均趋势评分", f"{home_summary['average_score']:.2f}")
            if home_rank_table.empty:
                render_empty_state("暂无趋势评分数据。")
            else:
                top_trends = home_rank_table.dropna(subset=["趋势分数"]).head(5)
                risk_watch = home_rank_table[home_rank_table["状态"] == "Weak"].head(5)
                st.markdown("**Top 5 趋势股票**")
                render_compact_table(top_trends, ["股票代码", "趋势分数", "状态", "收盘价", "数据来源"], 5)
                st.markdown("**风险观察股票**")
                if risk_watch.empty:
                    render_empty_state("当前没有 Weak 状态股票。")
                else:
                    render_compact_table(risk_watch, ["股票代码", "趋势分数", "状态", "收盘价"], 5)

        with account_col:
            render_section_header("模拟账户概览", "虚拟资金、持仓市值和浮动盈亏，仅用于演示。")
            if not home_paper_summary:
                render_empty_state("暂无模拟账户数据。")
            else:
                render_metric_row(
                    [
                        {"label": "现金", "value": f"{home_summary['paper_cash']:,.2f}"},
                        {"label": "持仓市值", "value": f"{home_summary['paper_positions_value']:,.2f}"},
                    ]
                )
                render_metric_row(
                    [
                        {"label": "总资产", "value": f"{home_summary['paper_total_value']:,.2f}"},
                        {"label": "浮动盈亏", "value": f"{home_summary['paper_unrealized_pnl']:,.2f}"},
                    ]
                )

        workflow_col, report_col = st.columns(2)
        with workflow_col:
            render_section_header("最近 workflow", "最近 3 条每日研究流程运行记录。")
            if home_workflow_runs.empty:
                render_empty_state("暂无 workflow 运行记录。")
            else:
                render_compact_table(
                    home_workflow_runs,
                    ["run_id", "market", "watchlist_name", "success_count", "failed_count", "report_id", "elapsed_seconds"],
                    3,
                )

        with report_col:
            render_section_header("最近报告", "最近 3 条日报或回测报告。")
            if home_reports.empty:
                render_empty_state("暂无历史报告。")
            else:
                render_compact_table(
                    home_reports,
                    ["report_id", "created_at", "report_type", "final_portfolio_value", "average_score"],
                    3,
                )

        render_section_header("常用功能入口", "按目标选择对应页面。")
        st.markdown(
            """
- 去“市场总览”查看趋势评分和研究信号。
- 去“组合回测”验证当前 watchlist 的历史表现。
- 去“每日流程”生成并保存每日研究报告。
- 去“系统健康”检查本地配置、缓存和运行环境。
"""
        )

    with rank_tab:
        render_section_header("市场总览", "查看当前自选股的趋势评分、研究信号和数据来源。")
        show_score_rules()
        rank_table = build_rank_table(market, symbols, use_cache=cache_enabled)
        if (rank_table["数据来源"] == "示例数据").any():
            st.warning(SAMPLE_WARNING)
        else:
            st.info("数据源：实时/历史行情数据")
        total_count = len(rank_table)
        strong_count = int((rank_table["状态"] == "Strong trend").sum())
        watchlist_count = int((rank_table["状态"] == "Watchlist").sum())
        weak_count = int((rank_table["状态"] == "Weak").sum())
        metric_cols = st.columns(4)
        metric_cols[0].metric("趋势评分数量", total_count)
        metric_cols[1].metric("Strong trend", strong_count)
        metric_cols[2].metric("Watchlist", watchlist_count)
        metric_cols[3].metric("Weak", weak_count)
        key_columns = ["股票代码", "趋势分数", "状态", "收盘价", "RSI14", "数据来源"]
        st.dataframe(rank_table[key_columns], use_container_width=True, hide_index=True)
        st.download_button(
            label="下载趋势评分 CSV",
            data=trend_scores_to_csv(rank_table),
            file_name="trend_scores.csv",
            mime="text/csv",
        )

    with strategy_lab_tab:
        render_section_header(
            "策略实验室",
            "管理本地策略参数预设，并基于历史数据运行研究回测。",
        )
        st.info("策略实验室用于管理本地策略参数预设，并基于历史数据进行研究回测。结果不代表未来收益，不构成投资建议。")

        try:
            strategy_presets = load_strategy_presets()
        except Exception as error:
            strategy_presets = {}
            st.error(f"无法读取策略预设：{error}")

        if not strategy_presets:
            render_empty_state("暂无策略预设。请先重置或保存一个策略预设。")
        else:
            render_section_header("策略预设", "默认只展示关键参数，便于快速比较。")
            presets_table = strategy_presets_to_dataframe(strategy_presets)
            render_compact_table(
                presets_table,
                ["name", "description", "min_score_to_buy", "min_score_to_hold", "max_position_pct", "rebalance_frequency"],
                10,
            )

            preset_names = sorted(strategy_presets)
            selected_preset_name = st.selectbox("选择策略预设", preset_names)
            selected_preset = strategy_presets[selected_preset_name]

            detail_col, edit_col = st.columns(2)
            with detail_col:
                render_section_header("当前预设详情", "查看所选策略参数。")
                render_parameter_summary(
                    {
                        "name": selected_preset.get("name"),
                        "strategy_type": selected_preset.get("strategy_type"),
                        "min_score_to_buy": selected_preset.get("min_score_to_buy"),
                        "min_score_to_hold": selected_preset.get("min_score_to_hold"),
                        "max_position_pct": selected_preset.get("max_position_pct"),
                        "rebalance_frequency": selected_preset.get("rebalance_frequency"),
                    }
                )
                st.caption(str(selected_preset.get("description", "")))

            with edit_col:
                render_section_header("编辑 / 保存预设", "保存为现有名称会覆盖该预设，保存为新名称会新增预设。")
                preset_name_input = st.text_input("preset name", value=selected_preset_name)
                preset_description_input = st.text_area(
                    "description",
                    value=str(selected_preset.get("description", "")),
                    height=90,
                )
                buy_threshold_input = st.number_input(
                    "min_score_to_buy",
                    min_value=0,
                    max_value=100,
                    value=int(selected_preset.get("min_score_to_buy", 80)),
                    step=1,
                )
                hold_threshold_input = st.number_input(
                    "min_score_to_hold",
                    min_value=0,
                    max_value=100,
                    value=int(selected_preset.get("min_score_to_hold", 60)),
                    step=1,
                )
                max_position_input = st.number_input(
                    "max_position_pct",
                    min_value=0.01,
                    max_value=1.0,
                    value=float(selected_preset.get("max_position_pct", 0.15)),
                    step=0.01,
                )
                rebalance_frequency_input = st.selectbox(
                    "rebalance_frequency",
                    ["monthly"],
                    index=0,
                )
                if st.button("保存策略预设"):
                    try:
                        save_strategy_preset(
                            preset_name_input,
                            {
                                "description": preset_description_input,
                                "strategy_type": "trend_score",
                                "min_score_to_buy": int(buy_threshold_input),
                                "min_score_to_hold": int(hold_threshold_input),
                                "max_position_pct": float(max_position_input),
                                "rebalance_frequency": rebalance_frequency_input,
                            },
                        )
                        st.success(f"策略预设已保存：{preset_name_input}")
                        st.rerun()
                    except Exception as error:
                        st.error(f"保存策略预设失败：{error}")

            render_section_header("删除预设", "默认策略禁止删除，避免误删基础配置。")
            if selected_preset_name in DEFAULT_PRESET_NAMES:
                st.info("当前选择的是默认策略，不能在 dashboard 中删除。")
            else:
                confirm_delete_preset = st.checkbox(f"确认删除策略预设 {selected_preset_name}")
                if st.button("删除策略预设"):
                    if not confirm_delete_preset:
                        st.error("请先勾选确认框，再删除策略预设。")
                    else:
                        try:
                            delete_strategy_preset(selected_preset_name)
                            st.success(f"已删除策略预设：{selected_preset_name}")
                            st.rerun()
                        except Exception as error:
                            st.error(f"删除策略预设失败：{error}")

            render_section_header("使用该策略运行组合回测", "使用当前 watchlist 和所选参数运行历史研究回测。")
            st.caption(f"当前 watchlist：{selected_watchlist}，股票数量：{len(symbols)}")
            if st.button("使用该策略运行组合回测"):
                try:
                    price_data, failed_symbols = load_price_data_for_symbols(market, symbols, use_cache=cache_enabled)
                    if failed_symbols:
                        st.warning(f"以下股票数据获取失败，已跳过：{', '.join(failed_symbols)}")
                    if not price_data:
                        st.error("没有可用于组合回测的行情数据。")
                    else:
                        strategy_result = run_portfolio_backtest(
                            price_data,
                            initial_cash=100000.0,
                            max_position_pct=float(selected_preset["max_position_pct"]),
                            rebalance_frequency=str(selected_preset["rebalance_frequency"]),
                            min_score_to_buy=int(selected_preset["min_score_to_buy"]),
                            min_score_to_hold=int(selected_preset["min_score_to_hold"]),
                        )
                        summary = strategy_result["summary"]
                        strategy_metrics = st.columns(5)
                        strategy_metrics[0].metric("总收益", format_return_pct(summary.get("total_return")))
                        strategy_metrics[1].metric("年化收益", format_return_pct(summary.get("annualized_return")))
                        strategy_metrics[2].metric("最大回撤", format_return_pct(summary.get("max_drawdown")))
                        strategy_metrics[3].metric("最终资产", f"{summary.get('final_portfolio_value', 0):,.2f}")
                        strategy_metrics[4].metric("交易次数", summary.get("number_of_trades", 0))

                        equity_curve = strategy_result["equity_curve"]
                        trades = strategy_result["trades"]
                        if not equity_curve.empty:
                            st.line_chart(equity_curve.set_index("date")[["total_value"]])
                            st.download_button(
                                label="下载 strategy_equity_curve.csv",
                                data=dataframe_to_csv(equity_curve),
                                file_name="strategy_equity_curve.csv",
                                mime="text/csv",
                            )
                        if trades.empty:
                            render_empty_state("本次策略回测没有交易记录。")
                        else:
                            render_compact_table(trades, None, 20)
                            st.download_button(
                                label="下载 strategy_trades.csv",
                                data=dataframe_to_csv(trades),
                                file_name="strategy_trades.csv",
                                mime="text/csv",
                            )
                except Exception as error:
                    st.error(f"策略组合回测失败：{error}")

    with strategy_comparison_tab:
        render_section_header(
            "策略对比",
            "比较多个本地策略预设在同一 watchlist 上的历史回测表现。",
        )
        st.info(STRATEGY_COMPARISON_WARNING)
        st.caption(f"当前市场：{market}；当前 watchlist：{selected_watchlist}；股票数量：{len(symbols)}")

        try:
            comparison_presets = load_strategy_presets()
        except Exception as error:
            comparison_presets = {}
            st.error(f"无法读取策略预设：{error}")

        if not comparison_presets:
            render_empty_state("暂无可用于对比的策略预设。")
        else:
            comparison_preset_names = sorted(comparison_presets)
            default_comparison_selection = [
                name for name in ["trend_default", "trend_conservative", "trend_aggressive"] if name in comparison_presets
            ]
            selected_comparison_presets = st.multiselect(
                "选择要对比的策略预设",
                comparison_preset_names,
                default=default_comparison_selection or comparison_preset_names[: min(3, len(comparison_preset_names))],
            )
            comparison_initial_cash = st.number_input(
                "策略对比初始资金",
                min_value=10_000,
                value=100_000,
                step=10_000,
                key="strategy_comparison_initial_cash",
            )

            if st.button("运行策略对比"):
                if not selected_comparison_presets:
                    st.warning("请至少选择一个策略预设。")
                else:
                    try:
                        price_data, failed_symbols = load_price_data_for_symbols(market, symbols, use_cache=cache_enabled)
                        if failed_symbols:
                            st.warning(f"以下股票数据获取失败，已跳过：{', '.join(failed_symbols)}")
                        if not price_data:
                            st.error("没有可用于策略对比的数据。")
                        else:
                            if any(is_sample_data(data) for data in price_data.values()):
                                st.warning(SAMPLE_WARNING)
                            selected_presets = {
                                name: comparison_presets[name]
                                for name in selected_comparison_presets
                                if name in comparison_presets
                            }
                            comparison_result = compare_strategy_presets(
                                selected_presets,
                                price_data,
                                initial_cash=float(comparison_initial_cash),
                            )
                            st.session_state["latest_strategy_comparison"] = comparison_result
                    except Exception as error:
                        st.error(f"策略对比运行失败：{error}")

            comparison_result = st.session_state.get("latest_strategy_comparison")
            if comparison_result:
                comparison_ranking = comparison_result.get("ranking", pd.DataFrame())
                comparison_failed = comparison_result.get("failed_presets", [])
                comparison_results = comparison_result.get("results", {})

                if comparison_ranking.empty:
                    st.error("所有策略对比均失败，暂无 ranking 结果。")
                else:
                    best_total = comparison_ranking.sort_values("total_return", ascending=False).iloc[0]
                    best_drawdown = comparison_ranking.sort_values("max_drawdown", ascending=False).iloc[0]
                    best_final = comparison_ranking.sort_values("final_portfolio_value", ascending=False).iloc[0]
                    render_metric_row(
                        [
                            {"label": "成功策略数", "value": len(comparison_results)},
                            {"label": "失败策略数", "value": len(comparison_failed)},
                            {"label": "最优总收益", "value": str(best_total["preset_name"]), "delta": format_return_pct(best_total["total_return"])},
                            {"label": "最低回撤", "value": str(best_drawdown["preset_name"]), "delta": format_return_pct(best_drawdown["max_drawdown"])},
                            {"label": "最终资产最高", "value": str(best_final["preset_name"]), "delta": f"{best_final['final_portfolio_value']:,.2f}"},
                        ]
                    )

                    display_ranking = comparison_ranking.copy()
                    for percent_column in ["total_return", "annualized_return", "max_drawdown"]:
                        display_ranking[percent_column] = display_ranking[percent_column].map(format_return_pct)
                    st.dataframe(display_ranking, use_container_width=True, hide_index=True)
                    st.download_button(
                        label="下载 strategy_comparison_ranking.csv",
                        data=dataframe_to_csv(comparison_ranking),
                        file_name="strategy_comparison_ranking.csv",
                        mime="text/csv",
                    )

                    equity_tables = []
                    for preset_name, result in comparison_results.items():
                        equity_curve = result.get("equity_curve", pd.DataFrame())
                        if not equity_curve.empty and {"date", "total_value"}.issubset(equity_curve.columns):
                            equity_tables.append(
                                equity_curve[["date", "total_value"]]
                                .rename(columns={"total_value": preset_name})
                                .set_index("date")
                            )
                    if equity_tables:
                        comparison_curve = pd.concat(equity_tables, axis=1).sort_index()
                        st.line_chart(comparison_curve)
                    else:
                        render_empty_state("暂无可展示的策略净值曲线。")

                    render_section_header("交易记录下载", "按策略下载对应的组合回测交易记录。")
                    for preset_name, result in comparison_results.items():
                        trades = result.get("trades", pd.DataFrame())
                        if trades.empty:
                            st.caption(f"{preset_name}：无交易记录。")
                        else:
                            st.download_button(
                                label=f"下载 {preset_name}_trades.csv",
                                data=dataframe_to_csv(trades),
                                file_name=f"{preset_name}_trades.csv",
                                mime="text/csv",
                            )

                    st.download_button(
                        label="下载 strategy_comparison_result.json",
                        data=strategy_comparison_to_json_bytes(comparison_result),
                        file_name="strategy_comparison_result.json",
                        mime="application/json",
                    )

                if comparison_failed:
                    st.warning("部分策略运行失败。")
                    st.dataframe(pd.DataFrame(comparison_failed), use_container_width=True, hide_index=True)

    with allocation_lab_tab:
        render_section_header(
            "组合配置实验室",
            "根据本地研究分数和风险参数生成目标仓位方案，并对比当前持仓差异。",
        )
        st.info(ALLOCATION_LAB_WARNING)
        st.caption(f"当前市场：{market}；当前 watchlist：{selected_watchlist}；股票数量：{len(symbols)}")

        try:
            allocation_presets = load_strategy_presets()
        except Exception as error:
            allocation_presets = {}
            st.warning(f"策略预设暂不可用，将使用默认趋势参数：{error}")

        allocation_preset_names = sorted(allocation_presets)
        default_allocation_preset = "trend_default" if "trend_default" in allocation_presets else None
        selected_allocation_preset_name = st.selectbox(
            "策略预设（用于读取研究参数）",
            allocation_preset_names,
            index=allocation_preset_names.index(default_allocation_preset) if default_allocation_preset else 0,
            disabled=not allocation_preset_names,
        ) if allocation_preset_names else None
        selected_allocation_preset = allocation_presets.get(selected_allocation_preset_name or "", {})

        allocation_col_a, allocation_col_b, allocation_col_c, allocation_col_d = st.columns(4)
        with allocation_col_a:
            allocation_portfolio_value = st.number_input(
                "组合总金额",
                min_value=10_000,
                value=100_000,
                step=10_000,
                key="allocation_portfolio_value",
            )
        with allocation_col_b:
            allocation_max_position_pct = st.number_input(
                "单股最大仓位（%）",
                min_value=1,
                max_value=100,
                value=int(float(selected_allocation_preset.get("max_position_pct", 0.2)) * 100),
                step=1,
                key="allocation_max_position_pct",
            )
        with allocation_col_c:
            allocation_min_score = st.number_input(
                "最低入选分数",
                min_value=0,
                max_value=100,
                value=int(selected_allocation_preset.get("min_score_to_hold", 60)),
                step=5,
                key="allocation_min_score",
            )
        with allocation_col_d:
            allocation_cash_buffer_pct = st.number_input(
                "现金缓冲（%）",
                min_value=0,
                max_value=90,
                value=10,
                step=5,
                key="allocation_cash_buffer_pct",
            )

        current_positions_text = st.text_area(
            "当前持仓（每行一个：symbol,数量）",
            value="",
            height=120,
            placeholder="AAPL,10\nMSFT,5\nNVDA,2",
            key="allocation_current_positions_text",
        )

        if st.button("生成组合配置方案"):
            if not symbols:
                st.info("当前 watchlist 为空，无法生成配置方案。")
            else:
                current_positions, position_warnings = parse_current_positions_text(current_positions_text)
                for warning in position_warnings:
                    st.warning(warning)
                try:
                    scores, prices, failed_symbols, used_sample_data = build_allocation_inputs(
                        market,
                        symbols,
                        use_cache=cache_enabled,
                    )
                    if used_sample_data:
                        st.warning(SAMPLE_WARNING)
                    if failed_symbols:
                        st.warning(f"以下股票无法用于配置计算：{', '.join(failed_symbols)}")
                    if not prices:
                        st.warning("没有可用于组合配置的价格数据。")

                    allocation_result = build_allocation_plan(
                        symbols=symbols,
                        scores=scores,
                        prices=prices,
                        current_positions=current_positions,
                        portfolio_value=float(allocation_portfolio_value),
                        max_position_pct=float(allocation_max_position_pct) / 100,
                        min_score=float(allocation_min_score),
                        cash_buffer_pct=float(allocation_cash_buffer_pct) / 100,
                    )
                    st.session_state["latest_allocation_plan"] = allocation_result
                except Exception as error:
                    st.error(f"生成组合配置方案失败：{error}")

        allocation_result = st.session_state.get("latest_allocation_plan")
        if allocation_result:
            summary = allocation_result.get("summary", {})
            allocation_rows = allocation_result.get("allocation", [])
            allocation_warnings = allocation_result.get("warnings", [])
            allocation_failed_symbols = allocation_result.get("failed_symbols", [])

            render_metric_row(
                [
                    {"label": "组合总金额", "value": f"{summary.get('portfolio_value', 0):,.2f}"},
                    {"label": "可投资金额", "value": f"{summary.get('investable_value', 0):,.2f}"},
                    {"label": "现金缓冲", "value": f"{summary.get('cash_buffer', 0):,.2f}"},
                    {"label": "入选股票数", "value": summary.get("selected_symbols", 0)},
                    {"label": "单股最大仓位", "value": format_return_pct(summary.get("max_position_pct"))},
                ]
            )

            if allocation_warnings:
                render_section_header("风险提示", "配置结果仅用于研究，不代表未来收益。")
                for warning in allocation_warnings:
                    st.warning(warning)
            if allocation_failed_symbols:
                st.warning("部分股票价格缺失或无效。")
                st.dataframe(pd.DataFrame(allocation_failed_symbols), use_container_width=True, hide_index=True)

            allocation_table = pd.DataFrame(allocation_rows)
            if allocation_table.empty:
                render_empty_state("暂无目标仓位数据。")
            else:
                display_columns = [
                    "symbol",
                    "score",
                    "price",
                    "target_weight",
                    "target_value",
                    "target_shares",
                    "current_shares",
                    "current_value",
                    "difference_value",
                ]
                st.dataframe(allocation_table[display_columns], use_container_width=True, hide_index=True)

                weight_chart = allocation_table[["symbol", "target_weight"]].set_index("symbol")
                st.bar_chart(weight_chart)

                value_chart = allocation_table[["symbol", "current_value", "target_value"]].set_index("symbol")
                st.bar_chart(value_chart)

                st.download_button(
                    label="下载 allocation_plan.csv",
                    data=dataframe_to_csv(allocation_table[display_columns]),
                    file_name="allocation_plan.csv",
                    mime="text/csv",
                )
                st.download_button(
                    label="下载 allocation_summary.json",
                    data=allocation_summary_to_json_bytes(allocation_result),
                    file_name="allocation_summary.json",
                    mime="application/json",
                )

    with chart_tab:
        render_section_header("单股分析", "查看单只股票的收盘价、均线和 RSI，用于研究趋势状态。")
        selected_symbol = st.selectbox("选择股票", symbols)
        try:
            data = load_data(market, selected_symbol, use_cache=cache_enabled)
            show_data_source_status(data)
            scored = add_trend_scores(data)
            st.line_chart(scored.set_index("date")[["close", "ma20", "ma60", "ma120"]])
            st.line_chart(scored.set_index("date")[["rsi14"]])
            st.dataframe(scored.tail(20), use_container_width=True, hide_index=True)
        except Exception as error:
            st.error(f"无法加载 {selected_symbol} 的数据：{error}")

    with backtest_tab:
        render_section_header("单股回测", "用固定趋势规则观察单只股票的历史表现。")
        backtest_symbol = st.selectbox("回测股票", symbols, key="backtest_symbol")
        initial_cash = st.number_input("初始资金", min_value=10_000, value=100_000, step=10_000)
        if st.button("运行回测"):
            try:
                data = load_data(market, backtest_symbol, use_cache=cache_enabled)
                show_data_source_status(data)
                result = run_simple_backtest(data, initial_cash=float(initial_cash))
                backtest_metrics = st.columns(4)
                backtest_metrics[0].metric("总收益", format_return_pct(result.get("total_return")))
                backtest_metrics[1].metric("年化收益", format_return_pct(result.get("annualized_return")))
                backtest_metrics[2].metric("最大回撤", format_return_pct(result.get("max_drawdown")))
                backtest_metrics[3].metric("最终资金", f"{float(result.get('final_portfolio_value', 0)):,.2f}")
                with st.expander("查看回测明细"):
                    st.json(result)
                st.session_state["latest_single_backtest_report"] = {
                    "parameters": {
                        "symbol": backtest_symbol,
                        "market": market,
                        "initial_cash": float(initial_cash),
                    },
                    "summary": result,
                }
            except Exception as error:
                st.error(f"无法完成 {backtest_symbol} 的回测：{error}")
        if "latest_single_backtest_report" in st.session_state:
            if st.button("保存单票回测报告"):
                try:
                    latest_report = st.session_state["latest_single_backtest_report"]
                    saved_report = save_backtest_report(
                        "single_stock_backtest",
                        latest_report["parameters"],
                        latest_report["summary"],
                    )
                    st.success(f"单票回测报告已保存：{saved_report['report_id']}")
                except Exception as error:
                    st.error(f"保存单票回测报告失败：{error}")

    with portfolio_tab:
        render_section_header("组合回测", "基于当前 watchlist 观察多股票组合的历史净值、交易和风险指标。")
        st.info(PORTFOLIO_BACKTEST_WARNING)
        portfolio_initial_cash = st.number_input(
            "组合回测初始资金",
            min_value=10_000,
            value=100_000,
            step=10_000,
            key="portfolio_initial_cash",
        )
        portfolio_max_position_pct = st.number_input(
            "单只股票最大仓位（%）",
            min_value=1,
            max_value=100,
            value=15,
            step=1,
            key="portfolio_max_position_pct",
        )
        portfolio_min_buy_score = st.number_input(
            "买入分数阈值",
            min_value=0,
            max_value=100,
            value=80,
            step=5,
            key="portfolio_min_buy_score",
        )
        portfolio_min_hold_score = st.number_input(
            "持有分数阈值",
            min_value=0,
            max_value=100,
            value=60,
            step=5,
            key="portfolio_min_hold_score",
        )

        if st.button("运行组合回测"):
            try:
                price_data, failed_symbols = load_price_data_for_symbols(market, symbols, use_cache=cache_enabled)
                if not price_data:
                    st.error("没有可用于组合回测的数据。")
                else:
                    if any(is_sample_data(data) for data in price_data.values()):
                        st.warning(SAMPLE_WARNING)
                    else:
                        st.info("数据源：实时/历史行情数据")

                    result = run_portfolio_backtest(
                        price_data,
                        initial_cash=float(portfolio_initial_cash),
                        max_position_pct=float(portfolio_max_position_pct) / 100,
                        min_score_to_buy=int(portfolio_min_buy_score),
                        min_score_to_hold=int(portfolio_min_hold_score),
                    )
                    summary = result["summary"]
                    skipped_symbols = sorted(set(failed_symbols + result["skipped_symbols"]))

                    total_col, annual_col, drawdown_col, final_col, trades_col = st.columns(5)
                    total_col.metric("总收益", format_return_pct(summary["total_return"]))
                    annual_col.metric("年化收益", format_return_pct(summary["annualized_return"]))
                    drawdown_col.metric("最大回撤", format_return_pct(summary["max_drawdown"]))
                    final_col.metric("最终资产", f"{summary['final_portfolio_value']:,.2f}")
                    trades_col.metric("交易次数", summary["number_of_trades"])

                    if skipped_symbols:
                        st.warning(f"跳过的股票：{', '.join(skipped_symbols)}")
                    else:
                        st.success("没有因数据不足或加载失败被跳过的股票。")

                    equity_curve = result["equity_curve"]
                    trades_table = result["trades"]
                    st.line_chart(equity_curve.set_index("date")[["total_value"]])
                    st.dataframe(trades_table, use_container_width=True, hide_index=True)
                    st.session_state["latest_portfolio_backtest_report"] = {
                        "parameters": {
                            "watchlist": symbols,
                            "market": market,
                            "initial_cash": float(portfolio_initial_cash),
                            "max_position_pct": float(portfolio_max_position_pct) / 100,
                            "min_score_to_buy": int(portfolio_min_buy_score),
                            "min_score_to_hold": int(portfolio_min_hold_score),
                        },
                        "summary": summary,
                        "equity_curve": equity_curve,
                        "trades": trades_table,
                    }

                    st.download_button(
                        label="下载组合净值 CSV",
                        data=dataframe_to_csv(equity_curve),
                        file_name="equity_curve.csv",
                        mime="text/csv",
                    )
                    st.download_button(
                        label="下载组合交易记录 CSV",
                        data=dataframe_to_csv(trades_table),
                        file_name="portfolio_trades.csv",
                        mime="text/csv",
                    )
            except Exception as error:
                st.error(f"组合回测失败：{error}")
        if "latest_portfolio_backtest_report" in st.session_state:
            if st.button("保存组合回测报告"):
                try:
                    latest_report = st.session_state["latest_portfolio_backtest_report"]
                    saved_report = save_backtest_report(
                        "portfolio_backtest",
                        latest_report["parameters"],
                        latest_report["summary"],
                        equity_curve=latest_report["equity_curve"],
                        trades=latest_report["trades"],
                    )
                    st.success(f"组合回测报告已保存：{saved_report['report_id']}")
                except Exception as error:
                    st.error(f"保存组合回测报告失败：{error}")

    with workflow_tab:
        render_section_header("每日流程", "基于当前市场和 watchlist，一键生成每日研究报告和运行记录。")
        st.info(DAILY_WORKFLOW_WARNING)
        workflow_market_code = market_code_from_label(market)
        workflow_col_market, workflow_col_watchlist, workflow_col_count = st.columns(3)
        workflow_col_market.metric("当前市场", workflow_market_code)
        workflow_col_watchlist.metric("当前 watchlist", selected_watchlist)
        workflow_col_count.metric("股票数量", len(symbols))

        if st.button("运行每日研究流程"):
            try:
                workflow_result = run_daily_research_workflow(
                    market=workflow_market_code,
                    watchlist_name=selected_watchlist,
                    symbols=symbols,
                    fetch_data_func=fetch_workflow_data,
                )
                saved_log = save_workflow_run_log(workflow_result)
                workflow_result["run_log_saved"] = True
                workflow_result["run_log_id"] = saved_log["run_id"]
                st.session_state["latest_daily_workflow_result"] = workflow_result
                st.success(f"运行记录已保存：{saved_log['run_id']}")
            except Exception as error:
                st.error(f"每日流程运行失败：{error}")

        if "latest_daily_workflow_result" in st.session_state:
            workflow_result = st.session_state["latest_daily_workflow_result"]
            if not workflow_result.get("success"):
                st.error(workflow_result.get("error", "每日流程失败，未保存空报告。"))
            else:
                st.success(f"每日流程完成，日报已保存：{workflow_result['report_id']}")

            failed_symbols = workflow_result.get("failed_symbols", [])
            if failed_symbols:
                st.warning(f"部分股票处理失败：{len(failed_symbols)} 个")
                st.dataframe(pd.DataFrame(failed_symbols), use_container_width=True, hide_index=True)
            workflow_warnings = workflow_result.get("warnings", [])
            if workflow_warnings:
                st.warning("部分股票使用了本地示例数据或存在数据源提示。")
                st.dataframe(pd.DataFrame({"warning": workflow_warnings}), use_container_width=True, hide_index=True)

            result_col_success, result_col_failed, result_col_report = st.columns(3)
            result_col_success.metric("成功处理股票数", workflow_result.get("success_count", 0))
            result_col_failed.metric("失败股票数", workflow_result.get("failed_count", len(failed_symbols)))
            result_col_report.metric("Report ID", workflow_result.get("report_id") or "未生成")
            st.caption(
                f"run_id: {workflow_result.get('run_id')} | elapsed_seconds: "
                f"{workflow_result.get('elapsed_seconds', 0):.2f}"
            )

            st.markdown("### 趋势评分摘要")
            st.json(workflow_result.get("summary", {}))

            workflow_scores = workflow_result.get("trend_scores", pd.DataFrame())
            if isinstance(workflow_scores, pd.DataFrame) and not workflow_scores.empty:
                top_scores = workflow_scores.sort_values("score", ascending=False).head(5)
                risk_scores = workflow_scores[
                    (workflow_scores["status"] == "Weak") | (workflow_scores["score"] < 40)
                ].sort_values("score", ascending=True)
                st.markdown("### Top 趋势股票")
                st.dataframe(top_scores, use_container_width=True, hide_index=True)
                st.markdown("### 风险观察股票")
                if risk_scores.empty:
                    st.info("本次流程没有 Weak 或低分风险观察股票。")
                else:
                    st.dataframe(risk_scores.head(10), use_container_width=True, hide_index=True)
                st.download_button(
                    label="下载本次趋势评分 CSV",
                    data=dataframe_to_csv(workflow_scores),
                    file_name="daily_workflow_trend_scores.csv",
                    mime="text/csv",
                )

            workflow_report = workflow_result.get("report")
            if workflow_report:
                st.download_button(
                    label="下载本次生成日报 JSON",
                    data=report_to_json_bytes(workflow_report),
                    file_name=f"{workflow_result['report_id']}.json",
                    mime="application/json",
                )

    with run_log_tab:
        render_section_header("运行记录", "查看每日流程的历史运行记录、成功股票和失败原因。")
        st.info(WORKFLOW_RUN_LOG_WARNING)
        try:
            run_logs = list_workflow_run_logs()
            if run_logs.empty:
                st.info("暂无 workflow 运行记录。运行每日流程后，这里会显示记录。")
            else:
                st.dataframe(run_logs, use_container_width=True, hide_index=True)
                st.download_button(
                    label="下载运行记录 summary CSV",
                    data=export_workflow_run_summary_csv().encode("utf-8-sig"),
                    file_name="workflow_run_summary.csv",
                    mime="text/csv",
                )
                selected_run_id = st.selectbox("选择 run_id", run_logs["run_id"].tolist())
                try:
                    run_log = load_workflow_run_log(selected_run_id)
                    st.markdown("### 运行详情")
                    detail_cols = st.columns(5)
                    detail_cols[0].metric("market", run_log.get("market", ""))
                    detail_cols[1].metric("watchlist", run_log.get("watchlist_name", ""))
                    detail_cols[2].metric("success_count", run_log.get("success_count", 0))
                    detail_cols[3].metric("failed_count", run_log.get("failed_count", 0))
                    detail_cols[4].metric("elapsed_seconds", f"{run_log.get('elapsed_seconds', 0):.2f}")

                    st.markdown("### success_symbols")
                    success_symbols = run_log.get("success_symbols", [])
                    if success_symbols:
                        st.dataframe(pd.DataFrame({"symbol": success_symbols}), use_container_width=True, hide_index=True)
                    else:
                        st.info("没有成功处理的股票。")

                    st.markdown("### failed_symbols")
                    failed_symbols = run_log.get("failed_symbols", [])
                    if failed_symbols:
                        st.dataframe(pd.DataFrame(failed_symbols), use_container_width=True, hide_index=True)
                    else:
                        st.info("没有失败股票。")

                    st.markdown("### error_message")
                    st.write(run_log.get("error_message") or run_log.get("error") or "无")
                    st.markdown("### report_id")
                    st.write(run_log.get("report_id") or "未生成")
                    st.markdown("### summary")
                    st.json(run_log.get("summary", {}))
                    st.download_button(
                        label="下载当前运行日志 JSON",
                        data=report_to_json_bytes(run_log),
                        file_name=f"{selected_run_id}.json",
                        mime="application/json",
                    )

                    confirm_delete_run = st.checkbox(
                        f"确认删除运行记录 {selected_run_id}",
                        key=f"delete_workflow_run_{selected_run_id}",
                    )
                    if st.button("删除当前运行记录"):
                        if not confirm_delete_run:
                            st.error("请先勾选确认框，再删除运行记录。")
                        else:
                            delete_workflow_run_log(selected_run_id)
                            st.success(f"已删除运行记录：{selected_run_id}")
                            st.rerun()
                except Exception as error:
                    st.error(f"无法读取运行记录详情：{error}")
        except Exception as error:
            st.error(f"运行记录中心加载失败：{error}")

    with data_quality_tab:
        render_section_header("数据质量", "检查本地缓存、数据完整性和行情 freshness。")
        st.info(PRICE_CACHE_WARNING)

        st.markdown("### 当前缓存列表")
        try:
            cached_symbols = list_cached_symbols()
            if cached_symbols.empty:
                st.info("暂无本地行情缓存。点击更新当前 watchlist 缓存后，这里会显示缓存文件。")
            else:
                display_cache = cached_symbols.drop(columns=["path"], errors="ignore")
                st.dataframe(display_cache, use_container_width=True, hide_index=True)
        except Exception as error:
            st.error(f"缓存列表读取失败：{error}")

        st.markdown("### 更新当前 watchlist 缓存")
        st.caption(f"当前市场：{market_code_from_label(market)}；当前 watchlist：{selected_watchlist}；股票数量：{len(symbols)}")
        if st.button("更新当前 watchlist 缓存"):
            quality_rows = []
            for symbol in symbols:
                try:
                    data = fetch_price_data(market, symbol, refresh_cache=True, use_cache=cache_enabled)
                    quality = build_data_quality_report(
                        market_code_from_label(market),
                        symbol,
                        data,
                        max_age_days=int(settings.get("cache", {}).get("max_age_days", 7)),
                    )
                    quality_rows.append(
                        {
                            "symbol": symbol,
                            "data_source": str(data.attrs.get("data_source", "unknown")),
                            "quality_status": quality["status"],
                            "rows": quality["row_count"],
                            "start_date": quality["start_date"],
                            "end_date": quality["end_date"],
                            "latest_close": quality["latest_close"],
                            "warnings": "; ".join(quality["warnings"]),
                            "errors": "; ".join(quality["errors"]),
                        }
                    )
                except Exception as error:
                    quality_rows.append(
                        {
                            "symbol": symbol,
                            "data_source": "unavailable",
                            "quality_status": "error",
                            "rows": 0,
                            "start_date": None,
                            "end_date": None,
                            "latest_close": None,
                            "warnings": "",
                            "errors": str(error),
                        }
                    )
            st.session_state["latest_data_quality_rows"] = quality_rows

        if "latest_data_quality_rows" in st.session_state:
            st.markdown("### 当前 watchlist 数据质量")
            quality_table = pd.DataFrame(st.session_state["latest_data_quality_rows"])
            st.dataframe(quality_table, use_container_width=True, hide_index=True)
            if (quality_table["data_source"] == "sample").any():
                st.warning(SAMPLE_WARNING)

        st.markdown("### 删除缓存文件")
        try:
            cached_symbols_for_delete = list_cached_symbols()
            if cached_symbols_for_delete.empty:
                st.info("没有可删除的缓存文件。")
            else:
                cache_choices = [
                    f"{row.market}:{row.symbol}"
                    for row in cached_symbols_for_delete.itertuples(index=False)
                ]
                selected_cache = st.selectbox("选择缓存", cache_choices)
                confirm_delete_cache = st.checkbox(
                    f"确认删除缓存 {selected_cache}",
                    key=f"delete_cache_{selected_cache}",
                )
                if st.button("删除当前缓存"):
                    if not confirm_delete_cache:
                        st.error("请先勾选确认框，再删除缓存。")
                    else:
                        cache_market, cache_symbol = selected_cache.split(":", 1)
                        delete_cached_price_data(cache_market, cache_symbol)
                        st.success(f"已删除缓存：{selected_cache}")
                        st.rerun()
        except Exception as error:
            st.error(f"缓存删除区域加载失败：{error}")

    with system_health_tab:
        render_section_header("系统健康", "检查本地配置、缓存、报告、示例数据、workflow 运行记录和安全边界。")
        st.info(SYSTEM_HEALTH_WARNING)

        if st.button("运行系统健康检查"):
            try:
                st.session_state["latest_system_health_check"] = run_system_health_check()
            except Exception as error:
                st.error(f"系统健康检查运行失败：{error}")

        if "latest_system_health_check" in st.session_state:
            health_result = st.session_state["latest_system_health_check"]
            overall_status = health_result.get("overall_status", "unknown")
            render_status_message(overall_status, f"整体状态：{format_health_status(overall_status)}")

            ok_col, warning_col, error_col = st.columns(3)
            ok_col.metric("OK", int(health_result.get("ok_count", 0)))
            warning_col.metric("Warning", int(health_result.get("warning_count", 0)))
            error_col.metric("Error", int(health_result.get("error_count", 0)))

            health_table = health_check_to_dataframe(health_result)
            st.dataframe(health_table, use_container_width=True, hide_index=True)

            for check in health_result.get("checks", []):
                check_message = f"{check.get('name')}: {check.get('message')}"
                if check.get("status") == "error":
                    st.error(check_message)
                elif check.get("status") == "warning":
                    st.warning(check_message)
                else:
                    st.success(check_message)

            health_json = json.dumps(health_result, ensure_ascii=False, indent=2)
            st.download_button(
                label="下载健康检查 JSON",
                data=health_json,
                file_name="system_health_check.json",
                mime="application/json",
            )
            st.download_button(
                label="下载健康检查 CSV",
                data=health_table.to_csv(index=False).encode("utf-8-sig"),
                file_name="system_health_check.csv",
                mime="text/csv",
            )
        else:
            st.info("点击按钮后运行一次本地系统健康检查。")

    with settings_tab:
        render_section_header("系统设置", "统一管理本地缓存、报告、模拟交易、dashboard 和 workflow 配置。")
        st.info(SETTINGS_WARNING)
        if settings_error is not None:
            st.error(f"当前 settings.json 读取失败：{settings_error}")

        st.markdown("### 当前配置")
        st.json(settings)

        st.markdown("### 修改常用设置")
        cache_enabled_input = st.checkbox(
            "启用本地行情缓存",
            value=bool(settings.get("cache", {}).get("enabled", True)),
        )
        cache_max_age_input = st.number_input(
            "缓存数据 freshness 最大天数",
            min_value=1,
            value=int(settings.get("cache", {}).get("max_age_days", 7)),
            step=1,
        )
        paper_initial_cash_input = st.number_input(
            "模拟交易默认初始资金",
            min_value=1.0,
            value=float(settings.get("paper_trading", {}).get("initial_cash", 100000.0)),
            step=1000.0,
        )
        dashboard_default_market_input = st.selectbox(
            "dashboard 默认市场",
            ["us", "cn"],
            index=["us", "cn"].index(str(settings.get("dashboard", {}).get("default_market", "us"))),
        )
        dashboard_show_disclaimer_input = st.checkbox(
            "显示全局免责声明",
            value=bool(settings.get("dashboard", {}).get("show_disclaimer", True)),
        )
        workflow_min_success_input = st.number_input(
            "每日 workflow 最少成功股票数",
            min_value=1,
            value=int(settings.get("workflow", {}).get("min_success_symbols", 1)),
            step=1,
        )

        if st.button("保存设置"):
            next_settings = {
                **settings,
                "cache": {
                    **settings.get("cache", {}),
                    "enabled": bool(cache_enabled_input),
                    "max_age_days": int(cache_max_age_input),
                },
                "paper_trading": {
                    **settings.get("paper_trading", {}),
                    "initial_cash": float(paper_initial_cash_input),
                },
                "dashboard": {
                    **settings.get("dashboard", {}),
                    "default_market": dashboard_default_market_input,
                    "show_disclaimer": bool(dashboard_show_disclaimer_input),
                },
                "workflow": {
                    **settings.get("workflow", {}),
                    "min_success_symbols": int(workflow_min_success_input),
                },
            }
            try:
                save_settings(next_settings)
                st.success("系统设置已保存。请刷新页面查看默认市场等启动类设置变化。")
            except Exception as error:
                st.error(f"保存系统设置失败：{error}")

        st.markdown("### 重置设置")
        confirm_reset_settings = st.checkbox("确认重置 settings.json 为默认配置。")
        if st.button("重置为默认设置"):
            if not confirm_reset_settings:
                st.error("请先勾选确认框，再重置系统设置。")
            else:
                try:
                    reset_settings()
                    st.success("系统设置已重置为默认配置。")
                    st.rerun()
                except Exception as error:
                    st.error(f"重置系统设置失败：{error}")

    with daily_tab:
        render_section_header("每日研究报告", "基于当前研究数据生成本地日报，不调用 AI API。")
        st.info(DAILY_REPORT_WARNING)
        if st.button("生成今日研究报告"):
            try:
                rank_table = build_rank_table(market, symbols, use_cache=cache_enabled)
                try:
                    portfolio = load_paper_portfolio()
                    latest_prices = latest_prices_for_positions(portfolio)
                    paper_summary = calculate_portfolio_summary(portfolio, latest_prices)
                except Exception as error:
                    paper_summary = {}
                    st.info(f"模拟账户摘要不可用：{error}")

                try:
                    backtest_summary = latest_backtest_summary()
                except Exception as error:
                    backtest_summary = {"note": f"最近回测摘要不可用：{error}"}

                daily_report = build_daily_research_report(
                    market=market,
                    watchlist_name=selected_watchlist,
                    trend_scores=rank_table,
                    data_source_summary=data_source_summary_from_rank_table(rank_table),
                    paper_portfolio_summary=paper_summary,
                    recent_backtest_summary=backtest_summary,
                )
                st.session_state["latest_daily_research_report"] = daily_report
            except Exception as error:
                st.error(f"生成日报失败：{error}")

        if "latest_daily_research_report" in st.session_state:
            daily_report = st.session_state["latest_daily_research_report"]
            markdown = daily_report_to_markdown(daily_report)
            st.markdown("### 日报预览")
            st.markdown(markdown)
            download_col, save_col = st.columns(2)
            with download_col:
                st.download_button(
                    label="下载当前日报 JSON",
                    data=report_to_json_bytes(daily_report),
                    file_name=f"{daily_report['report_id']}.json",
                    mime="application/json",
                )
                st.download_button(
                    label="下载当前日报 Markdown",
                    data=text_to_download(markdown),
                    file_name=f"{daily_report['report_id']}.md",
                    mime="text/markdown",
                )
            with save_col:
                if st.button("保存今日日报"):
                    try:
                        saved_report = save_daily_research_report(daily_report)
                        st.success(f"日报已保存：{saved_report['report_id']}")
                    except Exception as error:
                        st.error(f"保存日报失败：{error}")

        st.markdown("### 历史日报")
        try:
            daily_reports = list_daily_research_reports()
            if daily_reports.empty:
                st.info("暂无历史日报。生成并保存日报后，这里会显示记录。")
            else:
                st.dataframe(daily_reports, use_container_width=True, hide_index=True)
                st.download_button(
                    label="下载历史日报 summary CSV",
                    data=export_daily_report_summary_csv().encode("utf-8-sig"),
                    file_name="daily_report_summary.csv",
                    mime="text/csv",
                )
                selected_daily_report_id = st.selectbox("选择历史日报", daily_reports["report_id"].tolist())
                try:
                    historical_report = load_daily_research_report(selected_daily_report_id)
                    historical_markdown = daily_report_to_markdown(historical_report)
                    st.markdown("### 历史日报详情")
                    st.markdown(historical_markdown)
                    st.download_button(
                        label="下载历史日报 JSON",
                        data=report_to_json_bytes(historical_report),
                        file_name=f"{selected_daily_report_id}.json",
                        mime="application/json",
                    )
                    st.download_button(
                        label="下载历史日报 Markdown",
                        data=text_to_download(historical_markdown),
                        file_name=f"{selected_daily_report_id}.md",
                        mime="text/markdown",
                    )
                    confirm_delete_daily = st.checkbox(
                        f"确认删除日报 {selected_daily_report_id}",
                        key=f"delete_daily_report_{selected_daily_report_id}",
                    )
                    if st.button("删除当前日报"):
                        if not confirm_delete_daily:
                            st.error("请先勾选确认框，再删除日报。")
                        else:
                            delete_daily_research_report(selected_daily_report_id)
                            st.success(f"已删除日报：{selected_daily_report_id}")
                            st.rerun()
                except Exception as error:
                    st.error(f"无法读取历史日报：{error}")
        except Exception as error:
            st.error(f"日报中心加载失败：{error}")

    with report_tab:
        render_section_header("报告中心", "查看和导出已保存的回测报告与研究记录。")
        st.info(REPORT_CENTER_WARNING)
        try:
            reports_table = list_backtest_reports()
            if reports_table.empty:
                st.info("暂无历史回测报告。运行并保存回测后，这里会显示记录。")
            else:
                st.dataframe(reports_table, use_container_width=True, hide_index=True)
                st.download_button(
                    label="下载报告列表 summary CSV",
                    data=export_report_summary_csv().encode("utf-8-sig"),
                    file_name="backtest_report_summary.csv",
                    mime="text/csv",
                )
                selected_report_id = st.selectbox("选择报告", reports_table["report_id"].tolist())
                try:
                    report = load_backtest_report(selected_report_id)
                    metadata = {
                        "report_id": report.get("report_id"),
                        "created_at": report.get("created_at"),
                        "report_type": report.get("report_type"),
                        "parameters": report.get("parameters", {}),
                    }
                    st.markdown("### 报告 metadata")
                    st.json(metadata)
                    st.markdown("### 回测摘要")
                    st.json(report.get("summary", {}))

                    equity_records = report.get("equity_curve", [])
                    trades_records = report.get("trades", [])
                    if equity_records:
                        equity_table = pd.DataFrame(equity_records)
                        if "date" in equity_table.columns:
                            equity_table["date"] = pd.to_datetime(equity_table["date"], errors="coerce")
                            equity_table = equity_table.dropna(subset=["date"])
                        if {"date", "total_value"}.issubset(equity_table.columns):
                            st.markdown("### 净值曲线")
                            st.line_chart(equity_table.set_index("date")[["total_value"]])
                        st.dataframe(equity_table, use_container_width=True, hide_index=True)

                    if trades_records:
                        trades_table = pd.DataFrame(trades_records)
                        st.markdown("### 交易记录")
                        st.dataframe(trades_table, use_container_width=True, hide_index=True)
                        st.download_button(
                            label="下载当前报告 trades CSV",
                            data=report_records_to_csv(trades_records),
                            file_name=f"{selected_report_id}_trades.csv",
                            mime="text/csv",
                        )

                    st.download_button(
                        label="下载当前报告 JSON",
                        data=report_to_json_bytes(report),
                        file_name=f"{selected_report_id}.json",
                        mime="application/json",
                    )

                    confirm_delete_report = st.checkbox(
                        f"确认删除报告 {selected_report_id}",
                        key=f"delete_report_{selected_report_id}",
                    )
                    if st.button("删除当前报告"):
                        if not confirm_delete_report:
                            st.error("请先勾选确认框，再删除报告。")
                        else:
                            delete_backtest_report(selected_report_id)
                            st.success(f"已删除报告：{selected_report_id}")
                            st.rerun()
                except Exception as error:
                    st.error(f"无法读取报告详情：{error}")
        except Exception as error:
            st.error(f"报告中心加载失败：{error}")

    with paper_tab:
        render_section_header("模拟交易", "用虚拟资金记录买卖、持仓和交易流水，仅用于演示和学习。")
        st.info(PAPER_TRADING_WARNING)
        try:
            portfolio = load_paper_portfolio()
            latest_prices = latest_prices_for_positions(portfolio)
            summary = calculate_portfolio_summary(portfolio, latest_prices)
        except Exception as error:
            st.error(f"无法读取模拟账户：{error}")
            summary = calculate_portfolio_summary({"cash": 0.0, "positions": {}, "trades": []})
            portfolio = {"cash": 0.0, "positions": {}, "trades": []}

        cash_col, value_col, total_col, pnl_col, count_col = st.columns(5)
        cash_col.metric("当前现金", f"{summary['cash']:,.2f}")
        value_col.metric("持仓市值", f"{summary['positions_value']:,.2f}")
        total_col.metric("总资产", f"{summary['total_assets']:,.2f}")
        pnl_col.metric("浮动盈亏", f"{summary['unrealized_pnl']:,.2f}")
        count_col.metric("持仓数量", summary["position_count"])

        render_section_header("当前持仓", "查看模拟账户的持仓数量、成本和浮动盈亏。")
        positions_table = pd.DataFrame(summary["positions"])
        if positions_table.empty:
            st.info("当前没有模拟持仓。")
        else:
            st.dataframe(positions_table, use_container_width=True, hide_index=True)

        buy_col, sell_col = st.columns(2)
        with buy_col:
            st.markdown("### 模拟买入")
            buy_market = st.selectbox("买入市场", ["us", "cn"], key="paper_buy_market")
            buy_symbol = st.text_input("买入 symbol", value=symbols[0] if symbols else "", key="paper_buy_symbol")
            buy_price = st.number_input("买入价格", min_value=0.0, value=100.0, step=1.0, key="paper_buy_price")
            buy_quantity = st.number_input("买入数量", min_value=1, value=1, step=1, key="paper_buy_quantity")
            if st.button("模拟买入"):
                try:
                    buy_paper_position(buy_symbol, buy_price, int(buy_quantity), buy_market)
                    st.success("模拟买入成功。")
                    st.rerun()
                except Exception as error:
                    st.error(f"模拟买入失败：{error}")

        with sell_col:
            st.markdown("### 模拟卖出")
            position_symbols = sorted(portfolio.get("positions", {}))
            if position_symbols:
                sell_symbol = st.selectbox("卖出 symbol", position_symbols, key="paper_sell_symbol")
                sell_market = portfolio["positions"][sell_symbol].get("market", "us")
            else:
                sell_symbol = st.text_input("卖出 symbol", value="", key="paper_sell_symbol_text")
                sell_market = st.selectbox("卖出市场", ["us", "cn"], key="paper_sell_market")
            sell_price = st.number_input("卖出价格", min_value=0.0, value=100.0, step=1.0, key="paper_sell_price")
            sell_quantity = st.number_input("卖出数量", min_value=1, value=1, step=1, key="paper_sell_quantity")
            if st.button("模拟卖出"):
                try:
                    sell_paper_position(sell_symbol, sell_price, int(sell_quantity), sell_market)
                    st.success("模拟卖出成功。")
                    st.rerun()
                except Exception as error:
                    st.error(f"模拟卖出失败：{error}")

        render_section_header("交易记录", "查看最近 20 条模拟交易流水，并可导出 CSV。")
        trades = get_trade_history(portfolio)
        recent_trades = trades[-20:]
        if recent_trades:
            st.dataframe(pd.DataFrame(recent_trades), use_container_width=True, hide_index=True)
            st.download_button(
                label="下载交易记录 CSV",
                data=trades_to_csv(trades),
                file_name="paper_trades.csv",
                mime="text/csv",
            )
        else:
            st.info("暂无模拟交易记录。")

        render_section_header("重置模拟账户", "重置会清空本地模拟持仓和交易记录。")
        configured_initial_cash = float(settings.get("paper_trading", {}).get("initial_cash", 100000.0))
        confirm_reset = st.checkbox(
            f"确认重置模拟账户为 {configured_initial_cash:,.2f} 虚拟资金，并清空持仓和交易记录。"
        )
        if st.button("重置模拟账户"):
            if not confirm_reset:
                st.error("请先勾选确认框，再重置模拟账户。")
            else:
                try:
                    reset_paper_portfolio(initial_cash=configured_initial_cash)
                    st.success("模拟账户已重置。")
                    st.rerun()
                except Exception as error:
                    st.error(f"重置失败：{error}")

    with info_tab:
        render_section_header("说明", "了解趋势评分规则、数据来源和系统安全边界。")
        st.info("数据源：实时/历史行情数据或本地示例数据，取决于当前网络和数据源可用性。")
        show_score_rules()
        st.markdown(
            f"""
{DISCLAIMER}

{CACHE_NOTE}

当前版本仍然只做研究、历史回测、趋势观察、组合回测和模拟交易演示：

- 不连接真实券商
- 不自动下单
- 不做实盘交易
- 不保存 API key、secret、password、token 或券商凭证
- 不使用 AI 预测股价
- 自选股配置只保存股票代码列表，不保存账户信息
- 模拟交易只保存虚拟资金、持仓和交易记录，不连接真实券商
- 组合回测不包含手续费、滑点、停牌、涨跌停、分红或真实成交限制
- 回测报告只保存本地研究数据，不保存真实账户或券商凭证
- 每日研究报告只基于已有研究数据生成，不调用任何 AI API
- 每日流程只在用户点击按钮或本地 CLI 命令时运行，不提供后台定时任务
- 运行记录只保存本地研究流程运行信息，不保存真实账户或密钥
- 行情缓存只保存 OHLCV 数据，不保存账户信息、密钥或券商凭证
"""
        )


if __name__ == "__main__":
    main()
