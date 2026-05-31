from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.backtest.portfolio_backtest import run_portfolio_backtest
from src.backtest.simple_backtest import run_simple_backtest
from src.data.cn_data import get_cn_ohlcv
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
from src.reports.backtest_report import (
    delete_backtest_report,
    export_report_summary_csv,
    list_backtest_reports,
    load_backtest_report,
    save_backtest_report,
)
from src.strategies.trend_score import CN_WATCHLIST, US_WATCHLIST, add_trend_scores, latest_trend_score


st.set_page_config(page_title="山洞趋势量化系统", layout="wide")


SAMPLE_WARNING = "当前真实数据源获取失败，正在使用本地示例数据。示例数据仅用于功能演示，不代表真实行情，不构成投资建议。"
DISCLAIMER = "本系统仅用于学习、研究、历史回测和模拟交易演示，不构成投资建议。历史回测不代表未来收益。当前版本不连接真实券商，不自动下单。"
CACHE_NOTE = "行情数据使用缓存，默认缓存 1 小时。如需强制刷新，请重启应用或清理 Streamlit cache。"
PAPER_TRADING_WARNING = "模拟交易仅用于学习和功能演示，不代表真实交易，不构成投资建议，不会连接真实券商，也不会产生真实订单。"
PORTFOLIO_BACKTEST_WARNING = "组合回测仅用于历史研究和功能演示，不代表未来收益，不构成投资建议。"
REPORT_CENTER_WARNING = "历史回测报告仅用于研究和复盘，不代表未来收益，不构成投资建议。"


@st.cache_data(show_spinner=False, ttl=3600)
def load_data(market: str, symbol: str) -> pd.DataFrame:
    if market == "美股":
        return get_us_ohlcv(symbol)
    return get_cn_ohlcv(symbol)


def is_sample_data(data: pd.DataFrame) -> bool:
    return bool(data.attrs.get("is_sample_data", False))


def data_source_label(data: pd.DataFrame) -> str:
    if is_sample_data(data):
        return "示例数据"
    return "实时/历史行情数据"


def show_data_source_status(data: pd.DataFrame) -> None:
    if is_sample_data(data):
        st.warning(SAMPLE_WARNING)
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
    return data.to_csv(index=False).encode("utf-8-sig")


def report_to_json_bytes(report: dict) -> bytes:
    return json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")


def report_records_to_csv(records: list[dict]) -> bytes:
    return pd.DataFrame(records).to_csv(index=False).encode("utf-8-sig")


def parse_symbols_text(symbols_text: str) -> list[str]:
    raw_symbols = symbols_text.replace("，", ",").replace("\n", ",").split(",")
    return normalize_symbols(raw_symbols)


def default_watchlist_name(market: str) -> str:
    if market == "美股":
        return "us_default"
    return "cn_default"


def default_market_symbols(market: str) -> list[str]:
    if market == "美股":
        return US_WATCHLIST.copy()
    return CN_WATCHLIST.copy()


def build_rank_table(market: str, symbols: list[str]) -> pd.DataFrame:
    rows = []
    for symbol in symbols:
        try:
            data = load_data(market, symbol)
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


def load_price_data_for_symbols(market: str, symbols: list[str]) -> tuple[dict[str, pd.DataFrame], list[str]]:
    price_data = {}
    failed_symbols = []
    for symbol in symbols:
        try:
            price_data[symbol] = load_data(market, symbol)
        except Exception:
            failed_symbols.append(symbol)
    return price_data, failed_symbols


def market_label_from_code(market: str) -> str:
    if market.lower() == "cn":
        return "A股"
    return "美股"


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
    st.title("山洞趋势量化系统")
    st.warning(DISCLAIMER)

    market = st.sidebar.radio("市场", ["美股", "A股"])
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

    if not symbols:
        st.warning("股票池为空，请在左侧输入至少一个股票代码。")
        st.stop()

    rank_tab, chart_tab, backtest_tab, portfolio_tab, report_tab, paper_tab, info_tab = st.tabs(
        ["趋势评分", "单只股票分析", "简单回测", "组合回测", "报告中心", "模拟交易", "说明与风险提示"]
    )

    with rank_tab:
        st.subheader("趋势评分排名")
        show_score_rules()
        rank_table = build_rank_table(market, symbols)
        if (rank_table["数据来源"] == "示例数据").any():
            st.warning(SAMPLE_WARNING)
        else:
            st.info("数据源：实时/历史行情数据")
        st.dataframe(rank_table, use_container_width=True, hide_index=True)
        st.download_button(
            label="下载趋势评分 CSV",
            data=trend_scores_to_csv(rank_table),
            file_name="trend_scores.csv",
            mime="text/csv",
        )

    with chart_tab:
        st.subheader("收盘价、均线和 RSI")
        selected_symbol = st.selectbox("选择股票", symbols)
        try:
            data = load_data(market, selected_symbol)
            show_data_source_status(data)
            scored = add_trend_scores(data)
            st.line_chart(scored.set_index("date")[["close", "ma20", "ma60", "ma120"]])
            st.line_chart(scored.set_index("date")[["rsi14"]])
            st.dataframe(scored.tail(20), use_container_width=True, hide_index=True)
        except Exception as error:
            st.error(f"无法加载 {selected_symbol} 的数据：{error}")

    with backtest_tab:
        st.subheader("V1 简单回测")
        backtest_symbol = st.selectbox("回测股票", symbols, key="backtest_symbol")
        initial_cash = st.number_input("初始资金", min_value=10_000, value=100_000, step=10_000)
        if st.button("运行回测"):
            try:
                data = load_data(market, backtest_symbol)
                show_data_source_status(data)
                result = run_simple_backtest(data, initial_cash=float(initial_cash))
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
        st.subheader("V1.5 组合回测")
        st.warning(PORTFOLIO_BACKTEST_WARNING)
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
                price_data, failed_symbols = load_price_data_for_symbols(market, symbols)
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
                    total_col.metric("总收益", f"{summary['total_return']:.2%}")
                    annual_col.metric("年化收益", f"{summary['annualized_return']:.2%}")
                    drawdown_col.metric("最大回撤", f"{summary['max_drawdown']:.2%}")
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

    with report_tab:
        st.subheader("报告中心")
        st.warning(REPORT_CENTER_WARNING)
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
        st.subheader("本地模拟交易")
        st.warning(PAPER_TRADING_WARNING)
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

        st.subheader("当前持仓")
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

        st.subheader("交易记录")
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

        st.subheader("重置模拟账户")
        confirm_reset = st.checkbox("确认重置模拟账户为 100000 虚拟资金，并清空持仓和交易记录。")
        if st.button("重置模拟账户"):
            if not confirm_reset:
                st.error("请先勾选确认框，再重置模拟账户。")
            else:
                try:
                    reset_paper_portfolio()
                    st.success("模拟账户已重置。")
                    st.rerun()
                except Exception as error:
                    st.error(f"重置失败：{error}")

    with info_tab:
        st.subheader("说明与风险提示")
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
"""
        )


if __name__ == "__main__":
    main()
