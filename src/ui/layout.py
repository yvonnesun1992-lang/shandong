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

