# AGENTS.md

## Project Name

shandong

## Project Goal

Build a beginner-friendly A股 + 美股 trend-following quantitative investment system.

This project is for research, backtesting, signal generation, and portfolio analysis only.

Do not build real-money auto trading in V1.

## User Background

The user is a beginner in programming but has real investment experience.

The system should be easy to understand, easy to run, and easy to modify.

All code comments and README explanations should be beginner-friendly.

## Core Investment Philosophy

Use trend-following and risk control.

Do not use:
- High-frequency trading
- Intraday scalping
- AI prediction of stock prices
- Over-optimized parameters
- Real brokerage auto trading in V1

Focus on:
- Market trend
- Stock trend
- Relative strength
- Moving averages
- Volume confirmation
- Risk management
- Backtesting

## Markets

### A股

Use AkShare for Chinese stock data.

Start with:
- User-defined A股 watchlist
- Later expand to 沪深300
- Later expand to 中证1000

### 美股

Use yfinance for US stock data.

Start with:
- User-defined US watchlist
- Later expand to Nasdaq 100
- Later expand to S&P 500

## Strategy V1

Build a trend-following scoring strategy.

Use these indicators:

1. MA20
2. MA60
3. MA120
4. RSI14
5. Volume MA20
6. Recent price strength

## Scoring Logic

Each stock should get a score from 0 to 100.

Suggested scoring:

- Price above MA20: +15
- Price above MA60: +20
- Price above MA120: +20
- MA20 above MA60: +15
- MA60 above MA120: +15
- RSI between 50 and 75: +10
- Volume above Volume MA20: +5

Score interpretation:

- 80 to 100: Strong trend
- 60 to 79: Watchlist
- 40 to 59: Neutral
- Below 40: Weak / avoid

## Risk Control

Include simple risk control rules:

- Single stock max position: 10% to 15%
- Single trade risk should not exceed 2% of total capital
- Prefer cash when the market trend is weak
- Always calculate max drawdown in backtests

## Backtest V1

Create a simple backtest engine.

Basic rule:

Buy when:
- Trend score >= 80

Sell when:
- Trend score < 60
- Or price falls below MA60

Backtest output should include:

- Total return
- Annualized return
- Max drawdown
- Win rate
- Number of trades
- Final portfolio value

## Tech Stack

Use:

- Python 3.11+
- pandas
- numpy
- matplotlib
- yfinance
- akshare
- streamlit
- pytest

## Expected Project Structure

Create this structure:

```text
shandong/
├── app/
│   └── main.py
├── data/
│   └── README.md
├── notebooks/
│   └── README.md
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── us_data.py
│   │   └── cn_data.py
│   ├── indicators/
│   │   ├── __init__.py
│   │   └── technical.py
│   ├── strategies/
│   │   ├── __init__.py
│   │   └── trend_score.py
│   ├── backtest/
│   │   ├── __init__.py
│   │   └── simple_backtest.py
│   ├── risk/
│   │   ├── __init__.py
│   │   └── position.py
│   └── reports/
│       ├── __init__.py
│       └── daily_report.py
├── tests/
│   ├── test_indicators.py
│   └── test_trend_score.py
├── requirements.txt
├── README.md
├── AGENTS.md
└── .gitignore
```

## Commands

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

Run dashboard:

```bash
streamlit run app/main.py
```

## Coding Rules

* Write simple, readable Python.
* Add beginner-friendly comments.
* Keep functions small.
* Avoid complex architecture in V1.
* Do not hardcode API keys.
* Do not connect real brokerage accounts.
* Do not place real trades.
* Every important calculation should have a test.
* Prefer clarity over cleverness.

## Default Watchlists

Use these as sample stocks.

### US stocks

```python
US_WATCHLIST = [
    "NVDA",
    "AMD",
    "PLTR",
    "TSLA",
    "MSFT",
    "GOOGL",
    "META",
    "AVGO",
    "CORZ"
]
```

### A股 stocks

Use stock codes as strings:

```python
CN_WATCHLIST = [
    "300308",  # 中际旭创
    "300502",  # 新易盛
    "601138",  # 工业富联
    "002371",  # 北方华创
    "603986",  # 兆易创新
    "000977",  # 浪潮信息
    "002463",  # 沪电股份
    "300476",  # 胜宏科技
    "688256"   # 寒武纪
]
```

## Final Output Goal

After V1 is complete, the user should be able to:

1. Install dependencies.
2. Run a dashboard.
3. View trend scores for A股 and 美股.
4. Run a simple backtest.
5. Understand the code as a beginner.
