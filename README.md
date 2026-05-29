# 山洞 shandong

这是一个入门友好的 A股 + 美股趋势量化研究系统。

V1 只做研究、回测、趋势评分和仓位参考，不连接真实券商，不自动下单，也不使用机器学习预测股价。

## 项目能做什么

- 获取美股行情数据，数据源是 `yfinance`
- 获取 A股行情数据，数据源是 `akshare`
- 计算 MA20、MA60、MA120、RSI14、成交量 MA20
- 给股票打 0 到 100 的趋势分数
- 用简单规则做单只股票回测
- 用 Streamlit dashboard 查看评分、均线和 RSI

## 安装

建议先进入项目目录：

```bash
cd D:\HuaweiMoveData\Users\Yvonne\Documents\codex\shandong
```

安装依赖：

```bash
pip install -r requirements.txt
```

## 运行 dashboard

```bash
streamlit run app/main.py
```

打开后可以选择 A股或美股，查看默认股票池的趋势评分排名，也可以查看单只股票的收盘价、均线和 RSI。

## 运行测试

```bash
pytest
```

测试会检查均线、RSI 和趋势评分这些核心计算。

## 运行回测

现在回测模块可以在 Python 里直接调用：

```python
from src.data.us_data import get_us_ohlcv
from src.backtest.simple_backtest import run_simple_backtest

data = get_us_ohlcv("NVDA")
result = run_simple_backtest(data)
print(result)
```

回测输出包括：

- 总收益
- 年化收益
- 最大回撤
- 胜率
- 交易次数
- 最终资金

## 趋势评分规则

每只股票最高 100 分：

- 收盘价高于 MA20：+15
- 收盘价高于 MA60：+20
- 收盘价高于 MA120：+20
- MA20 高于 MA60：+15
- MA60 高于 MA120：+15
- RSI 在 50 到 75：+10
- 成交量高于成交量 MA20：+5

分数解释：

- 80 到 100：Strong trend
- 60 到 79：Watchlist
- 40 到 59：Neutral
- 40 以下：Weak

## 风险提醒

这个项目是学习和研究工具，不是投资建议。任何真实交易都需要你自己判断风险。
