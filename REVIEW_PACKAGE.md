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
- 最新代码验证提交：`026d9a4 Restore raw Python files to valid multiline format`
- 上一个提交：`cbcd5b0 Make raw files visibly multiline`
- Raw 刷新提交：`70c1a84 Force raw files to refresh LF formatting`
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
app/main.py lines=83
requirements.txt lines=7
.gitattributes lines=4
src/backtest/simple_backtest.py lines=70
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
app/main.py lines=83
first line='from __future__ import annotations'

requirements.txt lines=7
first line='pandas>=2.2'

.gitattributes lines=4
first line='*.md text eol=lf'

src/backtest/simple_backtest.py lines=70
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

## V1.1: sample data fallback and caching

V1.1 目标：

- 提高数据源稳定性。
- 当 `yfinance` 或 `akshare` 失败时，自动使用本地示例数据。
- 保证无网络或数据源失败时，dashboard 仍可以演示趋势评分、图表和回测。

新增文件：

```text
data/sample/us_NVDA.csv
data/sample/cn_300308.csv
src/data/sample_data.py
tests/test_sample_data.py
```

修改文件：

```text
app/main.py
src/data/us_data.py
src/data/cn_data.py
README.md
REVIEW_PACKAGE.md
```

实现内容：

- 示例 CSV 使用标准 OHLCV 字段：`date,open,high,low,close,volume`。
- 每个示例 CSV 有 180 行，日期递增，成交量为正数。
- `load_sample_ohlcv(market, symbol)` 支持：
  - `us + NVDA`
  - `cn + 300308`
- 美股数据优先走 `yfinance`，失败后 fallback 到 `data/sample/us_NVDA.csv`。
- A股数据优先走 `akshare`，失败后 fallback 到 `data/sample/cn_300308.csv`。
- fallback 数据通过 `DataFrame.attrs["is_sample_data"] = True` 标记。
- dashboard 使用 `st.cache_data(ttl=3600)` 缓存数据请求。
- dashboard 使用示例数据时显示 warning：

```text
当前真实数据源获取失败，正在使用本地示例数据。示例数据仅用于功能演示，不代表真实行情，不构成投资建议。
```

检查结果：

```text
py_compile: passed
pytest: 13 passed
dashboard: passed
```

py_compile 命令：

```bash
python -m py_compile app/main.py src/data/us_data.py src/data/cn_data.py src/data/sample_data.py src/indicators/technical.py src/strategies/trend_score.py src/backtest/simple_backtest.py src/risk/position.py src/reports/daily_report.py
```

pytest 结果：

```text
collected 13 items

tests/test_backtest.py .
tests/test_indicators.py ...
tests/test_sample_data.py ......
tests/test_trend_score.py ...

13 passed
```

dashboard 本地验证：

```text
http://localhost:8502 返回 200
趋势评分页：可显示示例数据评分和示例数据 warning
单只股票页：可显示 close、MA20、MA60、MA120、RSI14 图表
简单回测页：可使用示例数据跑通并显示回测结果
```

安全边界：

```text
是否使用真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.2: dashboard polish and CSV export

V1.2 目标：

- 把 Streamlit dashboard 优化成更适合演示的产品化界面。
- 保持核心策略不变。
- 继续禁止真实券商连接、自动下单、实盘交易和密钥保存。

新增文件：

```text
tests/test_dashboard_helpers.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

实现内容：

- 页面顶部增加全局免责声明。
- 趋势评分页、单只股票分析页、简单回测页显示数据源状态。
- 使用示例数据时显示 warning：

```text
当前真实数据源获取失败，正在使用本地示例数据。示例数据仅用于功能演示，不代表真实行情，不构成投资建议。
```

- 增加“趋势评分规则说明”可展开区域。
- 趋势评分排名支持导出 `trend_scores.csv`。
- sidebar 增加缓存说明：行情数据默认缓存 1 小时。
- 页面 tabs 调整为：
  - 趋势评分
  - 单只股票分析
  - 简单回测
  - 说明与风险提示
- 新增测试覆盖：
  - 趋势评分表可以转换为 CSV。
  - sample attrs 可以识别为示例数据。
  - 示例数据可以生成趋势评分结果。

检查结果：

```text
py_compile: passed
pytest: 16 passed
dashboard: passed
```

dashboard 本地验证：

```text
http://localhost:8503 返回 200
页面顶部免责声明：已显示
趋势评分页：已显示评分规则、数据源状态和 CSV 下载按钮
单只股票分析页：已显示数据源状态、收盘价/均线/RSI 图表
简单回测页：已显示数据源状态并可跑出回测结果
说明与风险提示页：已显示缓存说明和安全边界
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.3: local watchlist management

V1.3 目标：

- 让用户可以在 dashboard 中保存、加载、编辑自己的本地自选股列表。
- 避免每次运行 dashboard 都要手动输入股票池。
- 保持研究工具边界，不连接券商、不自动下单、不保存密钥。

新增文件：

```text
config/watchlists.json
src/data/watchlist_manager.py
tests/test_watchlist_manager.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
tests/test_dashboard_helpers.py
```

watchlist 功能说明：

- 默认配置文件：`config/watchlists.json`。
- 默认列表：
  - `us_default`
  - `cn_default`
- dashboard sidebar 支持：
  - 选择 watchlist
  - 编辑股票代码
  - 输入新 watchlist 名称
  - 保存自选股
- 股票代码会去空格、过滤空字符串、去重。
- 美股代码会转大写。
- A股数字代码会保留为 6 位字符串。
- watchlist 名称只允许字母、数字、下划线和短横线。
- 非法名称会被拒绝，不会被当作文件路径使用。
- 配置文件只保存股票代码列表，不保存账户、密码、API key 或券商凭证。

检查结果：

```text
py_compile: passed
pytest: 32 passed
dashboard: passed
```

dashboard 本地验证：

```text
http://localhost:8504 返回 200
sidebar：已显示自选股管理、watchlist 选择、新 watchlist 名称、股票池编辑框、保存自选股按钮
趋势评分页：可继续显示趋势评分和 CSV 下载按钮
数据源 fallback warning：可正常显示
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## V1.4: local paper trading portfolio

V1.4 目标：

- 增加一个本地模拟交易 / 纸上交易基础版。
- 用户可以用虚拟资金模拟买入、卖出、查看持仓、查看现金、查看盈亏和交易记录。
- 继续禁止真实券商连接、自动下单、实盘交易和密钥保存。

新增文件：

```text
config/paper_portfolio.json
src/paper_trading/__init__.py
src/paper_trading/portfolio.py
tests/test_paper_portfolio.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

模拟交易功能说明：

- 默认虚拟资金：`100000.0`。
- 本地文件：`config/paper_portfolio.json`。
- 支持虚拟买入：
  - 检查价格大于 0。
  - 检查数量大于 0。
  - 检查现金足够。
  - 更新平均成本。
  - 写入交易记录。
- 支持虚拟卖出：
  - 检查持仓数量足够。
  - 卖完后删除持仓。
  - 写入交易记录。
- dashboard 新增“模拟交易”tab：
  - 显示当前现金、持仓市值、总资产、浮动盈亏、持仓数量。
  - 显示持仓表。
  - 支持手动输入价格和数量进行模拟买卖。
  - 显示最近 20 条交易记录。
  - 支持下载交易记录 CSV。
  - 支持确认后重置模拟账户。
- 交易价格由用户手动输入，不会产生真实订单。
- 文件只保存虚拟资金、持仓和交易记录，不保存真实账户或券商凭证。

检查结果：

```text
py_compile: passed
pytest: 49 passed
dashboard: passed
```

dashboard 本地验证：

```text
http://localhost:8505 返回 200
模拟交易 tab：已显示免责声明
账户概览：已显示当前现金、持仓市值、总资产、浮动盈亏、持仓数量
持仓表：无持仓时显示提示
模拟买入/卖出：表单已显示
交易记录：无记录时显示提示
重置模拟账户：已显示确认 checkbox 和重置按钮
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```

## Fresh Clone 验证

已按人工 review 要求，从远程仓库重新 clone：

```bash
git clone git@github.com:yvonnesun1992-lang/shandong.git fresh-check
cd fresh-check
git checkout codex/v1-quant-system
python -m py_compile app/main.py src/backtest/simple_backtest.py
python -m pytest
```

结果：

```text
py_compile: passed
pytest: 7 passed
app/main.py lines=83 first='from __future__ import annotations'
src/backtest/simple_backtest.py lines=70 first='from __future__ import annotations'
requirements.txt lines=7 first='pandas>=2.2'
.gitattributes lines=4 first='*.md text eol=lf'
bad multiline string=False
```

## Remote / Branch 排查

按人工 reviewer 要求，未改代码前执行 Git 排查命令。

### git remote -v

```text
origin  git@github.com:yvonnesun1992-lang/shandong.git (fetch)
origin  git@github.com:yvonnesun1992-lang/shandong.git (push)
```

### git branch --show-current

```text
codex/v1-quant-system
```

### git status

```text
On branch codex/v1-quant-system
Your branch is up to date with 'origin/codex/v1-quant-system'.

nothing to commit, working tree clean
```

### git log -5 --oneline

```text
ba7321d Record fresh clone verification
026d9a4 Restore raw Python files to valid multiline format
cbcd5b0 Make raw files visibly multiline
3d13932 Update review package with latest raw check
70c1a84 Force raw files to refresh LF formatting
```

### git rev-parse HEAD

```text
ba7321d193841dd8a9d5beb9580db236ce006af4
```

### git ls-remote origin refs/heads/codex/v1-quant-system

```text
ba7321d193841dd8a9d5beb9580db236ce006af4 refs/heads/codex/v1-quant-system
```

### git diff origin/codex/v1-quant-system..HEAD --stat

```text
No diff.
```

结论：

- 当前分支是 `codex/v1-quant-system`。
- `HEAD` 等于 `origin/codex/v1-quant-system`。
- 最新提交已经 push 到 `yvonnesun1992-lang/shandong` 的 `codex/v1-quant-system` 分支。

## Explicit Push 后的 Raw 检查

执行：

```bash
git push origin HEAD:codex/v1-quant-system
```

push 结果：

```text
ba7321d..934c566 HEAD -> codex/v1-quant-system
```

随后按要求用远程 raw 链接检查：

```text
app/main.py:
83
'from __future__ import annotations\n\nimport pandas as pd\nimport streamlit as st\n\nfrom src.backtest.simple_backtest import run_simple_backtest\nfrom src.data.cn_data import get_cn_ohlcv\nfrom src.data.us_'

requirements.txt:
7
'pandas>=2.2\nnumpy>=1.26\nmatplotlib>=3.8\nyfinance>=0.2\nakshare>=1.14\nstreamlit>=1.36\npytest>=8.0\n'

.gitattributes:
4
'*.md text eol=lf\n*.py text eol=lf\n*.txt text eol=lf\n.gitignore text eol=lf\n'

src/backtest/simple_backtest.py:
70
'from __future__ import annotations\n\nimport pandas as pd\n\nfrom src.strategies.trend_score import add_trend_scores\n\n\ndef calculate_max_drawdown(equity: pd.Series) -> float:\n    """Maximum fall from a previous high point."""\n    running_high = equity.cummax()\n    drawdown = equity / running_high - 1\n  '
bad=False
```

确认：

```text
HEAD=934c5661b2675af0f9e6b1ad6610b9d103e708ca
origin/codex/v1-quant-system=934c5661b2675af0f9e6b1ad6610b9d103e708ca
```

## PR #6 文档 Unicode 安全复查

本次只复查和更新文档，不修改模拟交易业务逻辑。

复查文件：

- README.md
- REVIEW_PACKAGE.md

清理与验证结果：

- 已使用 Python 扫描 RLO、LRO、RLE、LRE、PDF、LRI、RLI、FSI、PDI。
- 已扫描 zero-width space、zero-width joiner、zero-width non-joiner、BOM。
- 已扫描 Unicode category Cf 和异常 control characters。
- 未发现需要删除的隐藏 Unicode、双向文本控制字符或异常控制字符。
- 已确认两个文档按 UTF-8 和 LF 换行保存。
- 未修改 `src/paper_trading/portfolio.py` 业务逻辑。
- 未连接真实券商。
- 未自动下单。
- 未加入 API key、secret、password、token。

验证命令：

```bash
python -m py_compile app/main.py src/data/us_data.py src/data/cn_data.py src/data/sample_data.py src/data/watchlist_manager.py src/paper_trading/portfolio.py src/indicators/technical.py src/strategies/trend_score.py src/backtest/simple_backtest.py src/risk/position.py src/reports/daily_report.py
python -m pytest
```

结果：

```text
py_compile: passed
pytest: 49 passed
```

## PR #6 GitHub Files Hidden Unicode 定位结论

用户反馈 ChatGPT 在 GitHub PR / Files changed 页面仍然看到：

```text
This file contains hidden or bidirectional Unicode text that may be interpreted or compiled differently than what appears below.
```

进一步定位结论：

- 已逐个检查 PR #6 相关文件：
  - README.md
  - REVIEW_PACKAGE.md
  - app/main.py
  - config/paper_portfolio.json
  - src/paper_trading/__init__.py
  - src/paper_trading/portfolio.py
  - tests/test_paper_portfolio.py
- 本地文件扫描未发现 hidden Unicode、bidi、zero-width、BOM、Unicode category Cf 或异常 control characters。
- 远程 raw 文件扫描也未发现上述风险字符。
- GitHub Files changed 页面的 HTML 源码中确实包含 hidden Unicode warning 文案，但它位于 GitHub 自带的 `<template>` 中。
- 该模板会被 GitHub 静态插入到 diff 页面中，不等于某个文件实际触发了警告。
- 实际可见页面检查结果：
  - `hasVisibleHiddenWarning=false`
  - `hasShowHiddenCharacters=false`
- 因此，如果审查工具直接搜索 GitHub HTML 源码，会误判；应以页面实际可见 warning 条、`Show hidden characters` 按钮或远程 raw 字符扫描为准。

最终验证：

```text
py_compile: passed
pytest: 49 passed
真实券商连接: 否
自动下单: 否
API key / secret / password / token: 否
PR merge: 否
```

## V1.5: portfolio backtesting and risk metrics

V1.5 目标：

- 增加组合回测功能。
- 基于当前 watchlist 对多个股票组成的组合做历史研究。
- 增加组合级风险指标。
- 继续禁止真实券商连接、自动下单、实盘交易和密钥保存。

新增文件：

```text
src/backtest/portfolio_backtest.py
src/risk/metrics.py
tests/test_portfolio_backtest.py
tests/test_risk_metrics.py
```

修改文件：

```text
app/main.py
README.md
REVIEW_PACKAGE.md
```

组合回测功能说明：

- 输入为多个股票的标准 OHLCV 数据。
- 使用现有趋势评分逻辑。
- 趋势分数大于等于买入阈值时进入候选池。
- 趋势分数低于持有阈值，或收盘价跌破 MA60 时卖出。
- 单只股票最大仓位默认 15%。
- 数据不足 120 行的股票会被跳过，并写入 `skipped_symbols`。
- 输出 `equity_curve`、`trades` 和 `summary`。
- `summary` 包含总收益、年化收益、最大回撤、交易次数、最终资产、现金和持仓市值。

dashboard 更新：

- 新增“组合回测”tab。
- 使用当前 watchlist 作为组合股票池。
- 支持设置初始资金、单只股票最大仓位、买入分数阈值和持有分数阈值。
- 展示总收益、年化收益、最大回撤、最终资产、交易次数和跳过股票。
- 展示组合净值曲线和交易记录表。
- 支持导出 `equity_curve.csv` 和 `portfolio_trades.csv`。
- 显示组合回测免责声明。

风险指标：

- `calculate_max_drawdown`
- `calculate_total_return`
- `calculate_annualized_return`

已知限制：

- 不包含手续费。
- 不包含滑点。
- 不处理停牌。
- 不处理涨跌停。
- 不处理分红。
- 不处理真实成交限制。
- 不做杠杆。
- 不做做空。

检查结果：

```text
py_compile: passed
pytest: 59 passed
dashboard: passed
```

安全边界：

```text
是否连接真实券商：否
是否自动下单：否
是否包含 API key/secret/password/token：否
是否使用 AI 预测股价：否
是否建议创建 PR：是
```
