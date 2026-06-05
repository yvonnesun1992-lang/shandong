from __future__ import annotations

import pandas as pd

from src.ui.layout import (
    dataframe_to_csv_bytes,
    format_data_source_label,
    format_health_status,
    format_return_pct,
)


def test_format_data_source_label_known_sources():
    assert format_data_source_label("cache") == "本地缓存"
    assert format_data_source_label("remote") == "实时/历史行情数据"
    assert format_data_source_label("sample") == "示例数据"


def test_format_health_status_known_statuses():
    assert format_health_status("ok") == "正常"
    assert format_health_status("warning") == "需关注"
    assert format_health_status("error") == "异常"


def test_format_return_pct_handles_common_values():
    assert format_return_pct(0.1234) == "12.34%"
    assert format_return_pct(-0.052) == "-5.20%"
    assert format_return_pct(0) == "0.00%"
    assert format_return_pct(None) == "N/A"


def test_dataframe_to_csv_bytes_outputs_header():
    data = pd.DataFrame([{"symbol": "NVDA", "score": 90}])

    csv_bytes = dataframe_to_csv_bytes(data)
    csv_text = csv_bytes.decode("utf-8-sig")

    assert isinstance(csv_bytes, bytes)
    assert "symbol,score" in csv_text
    assert "NVDA,90" in csv_text

