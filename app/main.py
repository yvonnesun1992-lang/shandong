from __future__ import annotations

import pandas as pd
import streamlit as st

from src.backtest.simple_backtest import run_simple_backtest
from src.data.cn_data import get_cn_ohlcv
from src.data.us_data import get_us_ohlcv
from src.strategies.trend_score import CN_WATCHLIST, US_WATCHLIST, add_trend_scores, latest_trend_score


st.set_page_config(page_title="山洞趋势量化系统", layout="wide")


@st.cache_data(show_spinner=False)
def load_data(market: str, symbol: str) -> pd.DataFrame:
    if market == "美股":
        return get_us_ohlcv(symbol)
    return get_cn_ohlcv(symbol)


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
                }
            )
        except Exception as error:
            rows.append({"股票代码": symbol, "趋势分数": None, "状态": f"数据错误: {error}", "收盘价": None, "RSI14": None})
    return pd.DataFrame(rows).sort_values("趋势分数", ascending=False, na_position="last")


st.title("山洞趋势量化系统")

market = st.sidebar.radio("市场", ["美股", "A股"])
default_watchlist = US_WATCHLIST if market == "美股" else CN_WATCHLIST
symbols_text = st.sidebar.text_area("股票池", value="\n".join(default_watchlist), height=220)
symbols = [line.strip().upper() for line in symbols_text.splitlines() if line.strip()]

rank_tab, chart_tab, backtest_tab = st.tabs(["趋势评分", "单只股票", "简单回测"])

with rank_tab:
    st.subheader("趋势评分排名")
    if st.button("刷新评分", type="primary"):
        st.cache_data.clear()
    st.dataframe(build_rank_table(market, symbols), use_container_width=True, hide_index=True)

with chart_tab:
    st.subheader("收盘价、均线和 RSI")
    selected_symbol = st.selectbox("选择股票", symbols)
    data = load_data(market, selected_symbol)
    scored = add_trend_scores(data)
    st.line_chart(scored.set_index("date")[["close", "ma20", "ma60", "ma120"]])
    st.line_chart(scored.set_index("date")[["rsi14"]])
    st.dataframe(scored.tail(20), use_container_width=True, hide_index=True)

with backtest_tab:
    st.subheader("V1 简单回测")
    backtest_symbol = st.selectbox("回测股票", symbols, key="backtest_symbol")
    initial_cash = st.number_input("初始资金", min_value=10_000, value=100_000, step=10_000)
    if st.button("运行回测"):
        data = load_data(market, backtest_symbol)
        result = run_simple_backtest(data, initial_cash=float(initial_cash))
        st.json(result)
