# 山洞 shandong

这是一个入门友好的 A股 + 美股趋势量化研究系统。

V1 只做研究、回测、趋势评分和仓位参考，不连接真实券商，不自动下单，也不使用机器学习预测股价。

## 产品定位

shandong 是一个股票量化研究与模拟交易平台原型。

当前版本仅用于学习、研究、历史回测和模拟交易，不连接真实券商，不自动下单，不构成投资建议。历史回测不代表未来收益。

## 项目能做什么

- 获取美股行情数据，数据源是 `yfinance`
- 获取 A股行情数据，数据源是 `akshare`
- 计算 MA20、MA60、MA120、RSI14、成交量 MA20
- 给股票打 0 到 100 的趋势分数
- 用简单规则做单只股票回测
- 基于 watchlist 做多股票组合回测
- 用 Streamlit dashboard 查看评分、均线和 RSI

## 快速启动

新手建议先阅读：

```text
docs/QUICK_START.md
```

推荐一键启动：

```bash
python scripts/start_dashboard.py
```

Windows 可以运行：

```bash
start_shandong.bat
```

启动前诊断：

```bash
python scripts/system_doctor.py
```

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

## V1.1 数据 fallback

系统优先使用真实行情数据：

- 美股：`yfinance`
- A股：`akshare`

如果真实数据源失败、返回空数据或缺少关键 OHLCV 字段，dashboard 会自动使用本地示例数据，让趋势评分、图表和简单回测仍然可以演示。

本地示例数据位于：

```text
data/sample/us_NVDA.csv
data/sample/cn_300308.csv
```

示例数据只用于演示和测试，不代表真实市场行情，也不是投资建议。dashboard 使用示例数据时会显示提示。

Streamlit 会缓存行情获取结果 1 小时，减少反复刷新时对 `yfinance` 和 `akshare` 的重复请求。

## V1.2 dashboard 产品化体验

V1.2 对 dashboard 做了轻量产品化优化：

- 页面顶部增加免责声明，明确不构成投资建议。
- 趋势评分、单只股票分析和简单回测页面都会显示数据源状态。
- 增加趋势评分规则说明，方便新用户理解分数来源。
- 趋势评分排名支持导出 `trend_scores.csv`。
- 页面结构调整为：趋势评分、单只股票分析、简单回测、说明与风险提示。
- sidebar 增加缓存说明：行情数据默认缓存 1 小时。

本系统仍然只用于学习、研究、历史回测和模拟交易演示，不连接真实券商，不自动下单。

## V1.3 本地自选股配置

V1.3 支持在 dashboard 中管理本地自选股：

- 可以从 sidebar 选择已有 watchlist。
- 可以编辑股票代码，一行一个或用逗号分隔。
- 可以保存当前自选股，也可以输入新名称保存为新的 watchlist。
- 默认配置文件位置：`config/watchlists.json`。

`config/watchlists.json` 只应该保存股票代码列表，不应保存任何账户、密码、API key、secret、token 或券商凭证。

本系统仅用于学习、研究、历史回测和模拟交易演示，不构成投资建议。

## V1.4 本地模拟交易

V1.4 支持本地模拟交易 / 纸上交易：

- 默认虚拟资金为 100000。
- 支持模拟买入、模拟卖出。
- 可以查看现金、持仓市值、总资产、浮动盈亏和持仓数量。
- 可以查看当前持仓和最近交易记录。
- 支持导出交易记录 CSV。
- 模拟交易数据保存在 `config/paper_portfolio.json`。

`config/paper_portfolio.json` 只保存虚拟账户数据，不保存任何真实账户、券商凭证、API key、secret、password 或 token。

模拟交易仅用于学习和功能演示，不会连接真实券商，不会自动下单，不构成投资建议。

文档已按 UTF-8 和 LF 换行保存，不应包含隐藏 Unicode 控制字符或双向文本控制字符。

## V1.5 组合回测

V1.5 支持基于当前 watchlist 的多股票组合回测：

- 使用趋势评分筛选组合候选股票。
- 支持设置初始资金、单只股票最大仓位、买入分数阈值和持有分数阈值。
- 输出组合收益曲线、总收益、年化收益、最大回撤、最终资产和交易次数。
- 支持导出 `equity_curve.csv` 和 `portfolio_trades.csv`。
- 数据不足 120 行的股票会被跳过，并在 dashboard 中提示。

V1.5 组合回测仍然是历史研究和功能演示，不代表未来收益，不构成投资建议。

当前组合回测不包含：

- 手续费
- 滑点
- 停牌
- 涨跌停
- 分红
- 真实成交限制
- 杠杆
- 做空

本系统不连接真实券商，不自动下单，不做实盘交易。

## V1.6 回测报告中心

V1.6 支持保存和查看本地回测报告：

- 支持保存单票回测报告。
- 支持保存组合回测报告。
- dashboard 新增“报告中心”页面。
- 可以查看历史报告列表、报告参数、回测摘要、净值曲线和交易记录。
- 支持下载当前报告 JSON。
- 支持下载当前报告交易记录 CSV。
- 支持下载全部报告 summary CSV。
- 报告保存在 `reports/backtests/`。

回测报告只用于研究和复盘，可以保存策略参数、股票代码、回测摘要、净值曲线和交易记录。

回测报告不应保存任何真实账户信息、券商凭证、API key、secret、password 或 token。

历史回测不代表未来收益。本系统不连接真实券商，不自动下单，不构成投资建议。

## V1.7 每日量化研究报告

V1.7 支持生成每日量化研究报告：

- 基于当前市场和当前 watchlist 生成研究日报。
- 日报包含趋势评分摘要、Top 趋势股票、风险观察股票、数据源状态、模拟账户摘要和最近回测摘要。
- dashboard 新增“每日研究报告”页面。
- 支持保存和查看历史日报。
- 支持导出日报 JSON。
- 支持导出日报 Markdown。
- 支持导出历史日报 summary CSV。
- 日报保存在 `reports/daily/`。

日报仅用于学习、研究和模拟交易演示，不构成投资建议。历史数据和模型评分不代表未来收益。

本功能不连接真实券商，不自动下单，不调用 OpenAI API 或任何外部 AI API。

## V1.8 一键每日研究流程

V1.8 支持本地一键每日研究流程：

- 自动读取当前 watchlist。
- 自动获取行情数据。
- 自动计算趋势评分。
- 自动生成并保存每日研究报告。
- dashboard 新增“每日流程”页面，可以手动点击运行。
- 新增 CLI 脚本，可以在命令行运行每日流程。

CLI 示例：

```bash
python scripts/run_daily_workflow.py --market us --watchlist us_default
```

每日流程只在用户手动点击按钮或运行本地命令时执行，不提供后台定时任务服务。

本功能不连接真实券商，不自动下单，不调用 OpenAI API 或任何外部 AI API，不构成投资建议。

## V1.9 workflow 运行记录

V1.9 支持每日 workflow 本地运行日志：

- 每次运行保存一个 run_id。
- 保存开始时间、结束时间、运行耗时、成功股票、失败股票、失败原因和 report_id。
- dashboard 新增“运行记录”页面。
- 可以查看历史运行记录列表。
- 可以查看单次运行详情。
- 可以下载当前运行日志 JSON。
- 可以下载运行记录 summary CSV。
- CLI 运行每日 workflow 后也会保存日志。
- 运行日志保存在 `reports/workflow_runs/`。

运行记录仅用于研究流程审计和复盘，不代表投资建议，不会产生真实交易。

本功能不连接真实券商，不自动下单，不调用 OpenAI API 或任何外部 AI API，不构成投资建议。

## V1.10 行情缓存与数据质量

V1.10 支持本地行情缓存和数据质量检查：

- 支持把标准 OHLCV 行情保存到 `data/cache/`。
- 支持从本地缓存读取行情，减少对 yfinance / akshare 的重复请求。
- 支持查看缓存列表，包括 market、symbol、行数、起止日期和文件大小。
- dashboard 新增“数据缓存与质量”页面。
- 支持更新当前 watchlist 的行情缓存。
- 支持删除单个缓存文件，删除前需要勾选确认。
- 支持检查数据是否缺字段、行数不足、日期不递增、价格异常、成交量异常、缺失 close 或最近日期过旧。
- 每日 workflow 会记录每只股票的数据来源：cache / remote / sample。

行情缓存只保存 OHLCV 行情数据，不保存任何账户信息、密钥或券商凭证。

数据缓存仅用于学习、研究和模拟交易演示，不代表实时行情，不构成投资建议。

本功能不连接真实券商，不自动下单，不调用 OpenAI API 或任何外部 AI API，不使用 AI 预测股价。

## V1.11 系统设置中心

V1.11 支持本地系统设置中心：

- 新增 `config/settings.json`。
- 新增 dashboard “系统设置”页面。
- 支持管理缓存配置、报告目录配置、模拟交易初始资金、dashboard 默认市场和 workflow 最少成功股票数。
- 支持保存设置。
- 支持重置为默认设置，重置前需要勾选确认。
- dashboard 默认市场优先读取 `settings.dashboard.default_market`。
- 模拟交易账户重置资金优先读取 `settings.paper_trading.initial_cash`。
- 数据质量 freshness 默认天数优先读取 `settings.cache.max_age_days`。
- 行情读取会参考 `settings.cache.enabled`。

配置文件只用于本地研究环境，不应保存任何真实账户、密码、API key、secret、password、token 或券商凭证。

本功能不连接真实券商，不自动下单，不调用 OpenAI API 或任何外部 AI API，不使用 AI 预测股价，不构成投资建议。

## V1.12 系统健康检查中心

V1.12 支持本地系统健康检查中心：

- 新增 `src/system/health_check.py`。
- dashboard 新增“系统健康”页面。
- 支持检查配置文件、缓存目录、报告目录、示例数据和 workflow 运行日志。
- 支持检查关键本地文件是否存在、JSON 是否损坏、示例 OHLCV 数据是否完整。
- 支持安全边界检查，确认运行代码中没有真实券商连接、自动下单、密钥保存或 AI API 调用风险。
- 支持导出健康检查 JSON。
- 支持导出健康检查 CSV。

系统健康检查仅用于本地研究环境诊断，不代表投资建议。

本功能不连接真实券商，不自动下单，不调用 OpenAI API 或任何外部 AI API，不使用 AI 预测股价，不构成投资建议。

## V1.13 一键启动与启动前自检

V1.13 增加本地启动工具：

- 新增 `scripts/system_doctor.py`，用于检查 Python 版本、关键依赖、关键目录、关键文件和系统健康状态。
- 新增 `scripts/start_dashboard.py`，先运行启动前检查，再启动 Streamlit dashboard。
- 新增 `start_shandong.bat`，适合 Windows 双击或命令行启动。
- 新增 `start_shandong.ps1`，适合 PowerShell 用户启动。
- 新增 `docs/QUICK_START.md`，面向新手说明安装、测试、启动和常见问题。

启动工具只用于本地研究环境，不连接真实券商，不自动下单，不调用 OpenAI API 或任何外部 AI API，不使用 AI 预测股价。

## V1.14 Dashboard UI 优化

V1.14 对 dashboard 做了轻量 UI 和页面结构优化：

- 页面标题统一为 `Shandong Quant Research`。
- 页面顶部增加统一产品副标题和研究风险提示。
- tabs 顺序调整为市场总览、单股分析、单股回测、组合回测、模拟交易、每日流程、报告、数据质量、运行记录、系统设置、系统健康和说明。
- 每个页面顶部增加简短说明，便于非技术用户理解。
- 趋势评分、单股回测、组合回测、模拟交易和系统健康使用更统一的指标展示。
- 新增 `src/ui/layout.py`，集中管理轻量 UI helper 和格式化函数。
- 文档与本次新增代码保持 UTF-8 + LF 文本格式。

本次优化不改变策略逻辑，不连接真实券商，不自动下单，不调用 OpenAI API 或任何外部 AI API。

## V1.15 首页 / 总览工作台

V1.15 为 dashboard 增加首页 / 总览工作台：

- 打开系统后优先查看市场、自选股、趋势评分和系统健康状态。
- 首页展示 Strong trend、Watchlist、Weak、平均趋势评分等研究概览。
- 首页展示模拟账户现金、持仓市值、总资产和浮动盈亏。
- 首页展示最近 workflow 运行记录和最近日报 / 回测报告。
- 首页提供市场总览、组合回测、每日流程和系统健康等常用功能入口说明。
- UI 继续保持简约、美观、大方、实用。

本次优化不改变策略逻辑，不连接真实券商，不自动下单，不调用 OpenAI API 或任何外部 AI API。

## V1.16 策略实验室

V1.16 增加“策略实验室”页面：

- 支持本地策略参数预设文件 `config/strategy_presets.json`。
- 支持读取、查看、保存和删除策略预设。
- 默认包含基础、保守、积极三组趋势策略参数。
- 支持使用当前 watchlist 和选中的策略预设运行组合回测。
- 展示组合回测总收益、年化收益、最大回撤、最终资产和交易次数。
- 支持导出策略回测净值曲线和交易记录 CSV。
- 页面继续保持简约、美观、大方、实用。

本功能不改变核心策略逻辑，不连接真实券商，不自动下单，不调用 OpenAI API 或任何外部 AI API，不构成投资建议。

## V1.17 策略对比中心

V1.17 增加“策略对比”页面：

- 支持选择多个本地策略预设，对同一个 watchlist 批量运行组合回测。
- 支持对比总收益、年化收益、最大回撤、交易次数和最终资产。
- 支持展示多个策略的净值曲线。
- 支持导出策略对比 ranking CSV、单个策略交易记录 CSV 和对比结果 JSON。
- 单个策略运行失败时会记录失败原因，不影响其他策略对比。
- 页面继续保持简约、美观、大方、实用。

本功能不改变核心策略逻辑，只调用现有策略预设和组合回测模块。

本功能不连接真实券商，不自动下单，不调用 OpenAI API 或任何外部 AI API，不构成投资建议。

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

V1 回测还很简单，不包含手续费、滑点、涨跌停、停牌、分红和真实成交限制。

V1 生成的趋势信号只用于研究和学习，不是投资建议。

V1 不连接券商、不自动下单、不做实盘交易。
