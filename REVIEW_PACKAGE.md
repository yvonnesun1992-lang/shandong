# REVIEW_PACKAGE.md

请帮我审查这个 GitHub Pull Request：

https://github.com/yvonnesun1992-lang/shandong/pull/1

## 审查目标

这是一个入门友好的 A股 + 美股趋势量化研究系统 V1。

请重点检查：

1. 项目结构是否合理。
2. 依赖是否合理，是否容易安装。
3. Python 文件是否有格式、缩进、SyntaxError 问题。
4. 趋势评分逻辑是否清晰、是否符合 AGENTS.md。
5. 简单回测逻辑是否有明显错误。
6. Streamlit dashboard 是否容易崩溃。
7. 是否存在真实交易、券商连接、自动下单、密钥泄露等危险逻辑。

## 当前分支和提交

- 分支：`codex/v1-quant-system`
- PR：`#1`
- 最新代码验证提交：`70c1a84 Force raw files to refresh LF formatting`
- 上一个提交：`5281d49 Add final review package`
- Raw 复查提交：`644b3c8 Reverify LF raw formatting`
- 格式规则提交：`ab5eb41 Enforce LF formatting and guard empty watchlists`
- 重要修复提交：`80636e2 Fix V1 install and runtime issues`

## 项目安全边界

V1 只做：

- 行情数据获取
- 技术指标计算
- 趋势评分
- 简单回测
- Streamlit 可视化
- 测试验证

V1 明确不做：

- 不连接真实券商
- 不自动下单
- 不做实盘交易
- 不使用 AI 预测股价
- 不保存或读取 API key、密码、券商凭证

## 最新格式修复说明

之前担心 GitHub raw 文件显示为一整行，导致 Python 代码不可运行。

当前已经完成以下修复和验证：

1. 强制把所有指定 `.py` 文件重新写成 UTF-8 + LF 多行格式。
2. 强制把 `requirements.txt`、`.gitattributes`、`.gitignore`、`README.md` 写成 LF 多行格式。
3. 新增 `.gitattributes`，固定文本文件换行：

```text
*.md text eol=lf
*.py text eol=lf
*.txt text eol=lf
.gitignore text eol=lf
```

4. 远程 GitHub raw 链接已经检查，不再是 `Total lines: 1`。

raw 检查结果：

```text
app/main.py lines=84
requirements.txt lines=8
.gitattributes lines=5
src/backtest/simple_backtest.py lines=71
simple_backtest bad multiline string=False
```

请使用这种 raw 路径检查分支，因为分支名里有 `/`：

```text
https://raw.githubusercontent.com/yvonnesun1992-lang/shandong/refs/heads/codex/v1-quant-system/app/main.py
https://raw.githubusercontent.com/yvonnesun1992-lang/shandong/refs/heads/codex/v1-quant-system/requirements.txt
https://raw.githubusercontent.com/yvonnesun1992-lang/shandong/refs/heads/codex/v1-quant-system/.gitattributes
```

## 项目结构

```text
shandong/
├── app/
│   └── main.py
├── data/
│   ├── .gitkeep
│   └── README.md
├── notebooks/
│   └── README.md
├── src/
│   ├── __init__.py
│   ├── backtest/
│   │   ├── __init__.py
│   │   └── simple_backtest.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── cn_data.py
│   │   └── us_data.py
│   ├── indicators/
│   │   ├── __init__.py
│   │   └── technical.py
│   ├── reports/
│   │   ├── __init__.py
│   │   └── daily_report.py
│   ├── risk/
│   │   ├── __init__.py
│   │   └── position.py
│   └── strategies/
│       ├── __init__.py
│       └── trend_score.py
├── tests/
│   ├── test_backtest.py
│   ├── test_indicators.py
│   └── test_trend_score.py
├── .gitignore
├── AGENTS.md
├── README.md
├── REVIEW_PACKAGE.md
└── requirements.txt
```

## requirements.txt

```text
pandas>=2.2
numpy>=1.26
matplotlib>=3.8
yfinance>=0.2
akshare>=1.14
streamlit>=1.36
pytest>=8.0
```

## 核心代码摘要

### app/main.py

Streamlit dashboard。

功能：

- 选择市场：`美股` 或 `A股`
- 编辑股票池
- 显示趋势评分排名
- 查看单只股票的收盘价、MA20、MA60、MA120、RSI14
- 运行单只股票简单回测

修复点：

- 单只股票图表区域加了 `try/except`
- 回测区域加了 `try/except`
- 如果 yfinance 或 akshare 数据源失败，页面显示错误提示，不让整个 dashboard 崩溃

### src/data/us_data.py

美股数据模块。

功能：

- 使用 `yfinance.download`
- 输入美股代码，例如 `NVDA`
- 输出标准 OHLCV：
  - `date`
  - `open`
  - `high`
  - `low`
  - `close`
  - `volume`

### src/data/cn_data.py

A股数据模块。

功能：

- 使用 `akshare.stock_zh_a_hist`
- 输入 A股代码，例如 `300308`
- 使用前复权：`adjust="qfq"`
- 输出标准 OHLCV：
  - `date`
  - `open`
  - `high`
  - `low`
  - `close`
  - `volume`

### src/indicators/technical.py

技术指标模块。

功能：

- `moving_average(series, window)`
- `rsi(series, window=14)`
- `add_technical_indicators(data)`

添加的指标：

- `ma20`
- `ma60`
- `ma120`
- `rsi14`
- `volume_ma20`

### src/strategies/trend_score.py

趋势评分策略。

默认股票池：

- 美股：`NVDA`, `AMD`, `PLTR`, `TSLA`, `MSFT`, `GOOGL`, `META`, `AVGO`, `CORZ`
- A股：`300308`, `300502`, `601138`, `002371`, `603986`, `000977`, `002463`, `300476`, `688256`

评分逻辑：

- 收盘价高于 MA20：+15
- 收盘价高于 MA60：+20
- 收盘价高于 MA120：+20
- MA20 高于 MA60：+15
- MA60 高于 MA120：+15
- RSI 在 50 到 75：+10
- 成交量高于成交量 MA20：+5

状态：

- 80 到 100：`Strong trend`
- 60 到 79：`Watchlist`
- 40 到 59：`Neutral`
- 40 以下：`Weak`

### src/backtest/simple_backtest.py

简单单只股票回测模块。

买入条件：

- 趋势分数 `>= 80`

卖出条件：

- 趋势分数 `< 60`
- 或收盘价跌破 MA60

输出：

- `total_return`
- `annualized_return`
- `max_drawdown`
- `win_rate`
- `number_of_trades`
- `final_portfolio_value`

重要修复：

- 原来买入时使用全部现金。
- 现在 V1 最多只使用 `15%` 初始资金买入单只股票。
- 这样避免了单只股票满仓，符合风险控制方向。
- 错误字符串已保持单行，不存在跨行未闭合字符串：

```python
raise ValueError("Not enough data for backtest. Need at least 120 rows.")
```

注意：

- V1 回测不包含手续费。
- V1 回测不包含滑点。
- V1 回测不处理涨跌停、停牌、分红、真实成交限制。

### src/risk/position.py

风险控制模块。

功能：

- `max_position_value(total_capital, max_position_pct=0.15)`
- `position_size_by_risk(total_capital, entry_price, stop_price, risk_pct=0.02)`
- `suggested_position_size(...)`

当前回测 V1 先直接使用 15% 初始资金上限，后续再逐步接入完整 risk 模块。

### src/reports/daily_report.py

报告模块。

功能：

- 输入多只股票的数据
- 输出按趋势分数排序的表格

## 测试结果

运行命令：

```bash
python -m pytest
```

结果：

```text
collected 7 items

tests/test_backtest.py .
tests/test_indicators.py ...
tests/test_trend_score.py ...

7 passed
```

## 最终本地检查结果

已运行：

```bash
git add --renormalize .
git diff --check
python -m py_compile app/main.py src/data/us_data.py src/data/cn_data.py src/indicators/technical.py src/strategies/trend_score.py src/backtest/simple_backtest.py src/risk/position.py src/reports/daily_report.py
python -m pytest
```

结果：

```text
git diff --check: passed
py_compile: passed
pytest: 7 passed
```

## Python 编译检查

运行命令：

```bash
python -m py_compile app/main.py src/data/us_data.py src/data/cn_data.py src/indicators/technical.py src/strategies/trend_score.py src/backtest/simple_backtest.py src/risk/position.py src/reports/daily_report.py
```

结果：

```text
passed
```

没有发现 `SyntaxError`。

## 最终远程 Raw 检查结果

检查命令使用 `curl` 直接读取 GitHub raw，不使用本地文件。

结果：

```text
app/main.py lines=84
first line='from __future__ import annotations'

requirements.txt lines=8
first line='pandas>=2.2'

.gitattributes lines=5
first line='*.md text eol=lf'

src/backtest/simple_backtest.py lines=71
first line='from __future__ import annotations'
bad multiline string=False
```

这些结果满足：

1. `app/main.py lines > 1`
2. `requirements.txt lines >= 7`
3. `.gitattributes lines >= 4`
4. `src/backtest/simple_backtest.py lines > 1`
5. `simple_backtest.py` 不存在跨行未闭合字符串

## Streamlit 空股票池保护

`app/main.py` 已经增加空股票池保护：

```python
if not symbols:
    st.warning("股票池为空，请在左侧输入至少一个股票代码。")
    st.stop()
```

## Dashboard 检查

运行命令：

```bash
streamlit run app/main.py
```

本地检查：

```text
http://localhost:8501 返回 200
```

## 已知限制

1. V1 数据依赖外部数据源，`yfinance` 或 `akshare` 网络失败时可能无法获取行情。
2. V1 回测是单只股票简单回测，不是完整投资组合回测。
3. V1 没有手续费、滑点、停牌、涨跌停、分红处理。
4. V1 没有交易日历和市场状态判断。
5. V1 dashboard 主要用于学习和查看结果，不是生产级投研系统。

## 请重点帮我检查的问题

1. GitHub raw 文件是否确实已经是多行，不是 `Total lines: 1`。
2. `app/main.py` 是否可以正常运行，空股票池保护是否合理。
3. 回测中 15% 仓位限制是否写得合理。
4. RSI 计算有没有明显问题。
5. A股和美股 OHLCV 标准化是否容易出错。
6. Streamlit 的错误处理是否足够避免页面崩溃。
7. 测试是否覆盖了最重要的计算。
8. 是否还有任何真实交易或券商连接风险。
9. README 是否已经把风险边界说清楚。
10. 这个 PR 是否可以 merge。

## 给 ChatGPT 的一句话请求

请帮我审查 PR #1，重点确认 GitHub raw 文件已经是正常多行代码、项目可安装可测试可运行、没有真实交易或券商连接风险。如果仍看到 `Total lines: 1`，请不要建议 merge。

## 最终状态

- 已 push 到 PR #1 的 `codex/v1-quant-system` 分支。
- 已确认没有 merge PR。
- 未发现真实交易、券商连接、自动下单、API key、secret、password 风险。
- 建议人工 reviewer 继续审查业务逻辑和可维护性；如 reviewer 也确认 raw 多行、测试通过、风险边界清楚，可以再考虑 merge。
