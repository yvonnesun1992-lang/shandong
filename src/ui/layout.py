from __future__ import annotations

import pandas as pd
import streamlit as st


RISK_DISCLAIMER = "仅用于学习、研究、历史回测和模拟交易演示，不构成投资建议。"


def render_page_header(title: str, subtitle: str | None = None) -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def render_risk_disclaimer() -> None:
    st.info(RISK_DISCLAIMER)


def render_section_header(title: str, description: str | None = None) -> None:
    st.subheader(title)
    if description:
        st.caption(description)


def render_status_message(status: str, message: str) -> None:
    normalized = str(status).strip().lower()
    if normalized == "error":
        st.error(message)
    elif normalized == "warning":
        st.warning(message)
    elif normalized == "ok":
        st.success(message)
    else:
        st.info(message)


def format_data_source_label(source: str) -> str:
    labels = {
        "cache": "本地缓存",
        "remote": "实时/历史行情数据",
        "sample": "示例数据",
        "sample_fallback": "示例数据",
    }
    normalized = str(source).strip().lower()
    return labels.get(normalized, str(source))


def format_health_status(status: str) -> str:
    labels = {
        "ok": "正常",
        "warning": "需关注",
        "error": "异常",
    }
    normalized = str(status).strip().lower()
    return labels.get(normalized, str(status))


def format_return_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{float(value) * 100:.2f}%"


def dataframe_to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def render_metric_row(metrics: list[dict]) -> None:
    if not metrics:
        return
    columns = st.columns(len(metrics))
    for column, metric in zip(columns, metrics):
        column.metric(
            str(metric.get("label", "")),
            metric.get("value", "N/A"),
            metric.get("delta"),
        )


def render_empty_state(message: str) -> None:
    st.info(message)


def render_compact_table(dataframe: pd.DataFrame, columns: list[str] | None = None, max_rows: int = 10) -> None:
    if dataframe is None or dataframe.empty:
        render_empty_state("暂无可展示数据。")
        return
    display = dataframe.copy()
    if columns:
        available_columns = [column for column in columns if column in display.columns]
        if available_columns:
            display = display[available_columns]
    st.dataframe(display.head(max_rows), use_container_width=True, hide_index=True)
