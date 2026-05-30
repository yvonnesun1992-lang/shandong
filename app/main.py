from __future__ import annotations

import pandas as pd
import streamlit as st

from src.backtest.simple_backtest import run_simple_backtest
from src.data.cn_data import get_cn_ohlcv
from src.data.us_data import get_us_ohlcv
from src.data.watchlist_manager import load_watchlists, normalize_symbols, save_watchlist, validate_watchlist_name
from src.strategies.trend_score import CN_WATCHLIST, US_WATCHLIST, add_trend_scores, latest_trend_score


st.set_page_config(page_title="山洞趋势量化系统", layout="wide")


SAMPLE_WARNING = "当前真实数据源获取失败，正在使用本地示例数据。示例数据仅用于功能演示，不代表真实行情，不构成投资建议。"
DISCLAIMER = "本系统仅用于学习、研究、历史回测和模拟交易演示，不构成投资建议。历史回测不代表未来收益。当前版本不连接真实券商，不自动下单。"
CACHE_NOTE = "行情数据使用缓存，默认缓存 1 小时。如需强制刷新，请重启应用或清理 Streamlit cache。"


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

    rank_tab, chart_tab, backtest_tab, info_tab = st.tabs(["趋势评分", "单只股票分析", "简单回测", "说明与风险提示"])

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
            except Exception as error:
                st.error(f"无法完成 {backtest_symbol} 的回测：{error}")

    with info_tab:
        st.subheader("说明与风险提示")
        st.info("数据源：实时/历史行情数据或本地示例数据，取决于当前网络和数据源可用性。")
        show_score_rules()
        st.markdown(
            f"""
{DISCLAIMER}

{CACHE_NOTE}

V1.3 仍然只做研究、历史回测、趋势观察和模拟交易演示：

- 不连接真实券商
- 不自动下单
- 不做实盘交易
- 不保存 API key、secret、password、token 或券商凭证
- 不使用 AI 预测股价
- 自选股配置只保存股票代码列表，不保存账户信息
"""
        )


if __name__ == "__main__":
    main()
