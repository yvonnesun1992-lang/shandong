# Technical Architecture

This document describes a staged architecture for shandong as it grows from a local research app into a multi-user research and paper-trading platform.

## Short Term Architecture

The short-term system should stay simple and local-first.

### Stack

- Streamlit dashboard.
- Python.
- pandas and numpy.
- yfinance for US stock data.
- AkShare for A-share data.
- Local CSV or Parquet cache.
- pytest for core calculation tests.

### Responsibilities

- `app/`: Streamlit user interface.
- `src/data/`: market data loaders and fallback logic.
- `src/indicators/`: technical indicator calculations.
- `src/strategies/`: scoring and strategy rules.
- `src/backtest/`: simple backtest engine.
- `src/risk/`: position sizing and risk helpers.
- `data/`: local cache and sample data.

### Design Notes

- Keep functions small and beginner-friendly.
- Use standard OHLCV columns across all modules.
- Prefer local sample data when external data fails.
- Avoid hidden credentials or API keys.

## Medium Term Architecture

The medium-term architecture should separate backend logic from the dashboard.

### Stack

- FastAPI backend.
- PostgreSQL database.
- Redis cache.
- APScheduler or Celery for scheduled jobs.
- Streamlit or a simple web dashboard.
- SQLAlchemy or another clear ORM layer.

### Backend Services

- Market data service.
- Indicator service.
- Strategy scoring service.
- Backtest service.
- Paper portfolio service.
- Report service.

### Data Flow

1. Scheduled jobs fetch or refresh market data.
2. Data is normalized into standard OHLCV format.
3. Indicators and scores are calculated from normalized data.
4. Dashboard reads prepared results from backend APIs.
5. Users save watchlists, strategy settings, and backtest results.

## Long Term Architecture

The long-term architecture should support SaaS usage, teams, and paper trading.

### Stack

- React or Next.js frontend.
- FastAPI backend.
- PostgreSQL.
- Redis.
- Docker.
- Cloud server deployment.
- Multi-user permission system.
- Paper trading engine.
- Strategy backtest engine.
- Report system.

### Key Components

- Authentication and user management.
- Watchlist management.
- Market data ingestion.
- Historical price storage.
- Strategy definition and versioning.
- Backtest execution queue.
- Paper trading ledger.
- Portfolio analytics.
- Risk event monitoring.
- Subscription and entitlement management.

## Database Draft

### users

- `id`
- `email`
- `display_name`
- `created_at`
- `status`

Stores platform users.

### watchlists

- `id`
- `user_id`
- `name`
- `created_at`
- `updated_at`

Stores user-defined watchlists.

### symbols

- `id`
- `market`
- `ticker`
- `name`
- `currency`
- `is_active`

Stores supported securities.

### price_bars

- `id`
- `symbol_id`
- `date`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `source`

Stores normalized OHLCV bars.

### strategies

- `id`
- `user_id`
- `name`
- `strategy_type`
- `parameters_json`
- `created_at`
- `updated_at`

Stores strategy configurations.

### backtests

- `id`
- `user_id`
- `strategy_id`
- `symbol_id`
- `start_date`
- `end_date`
- `initial_capital`
- `result_json`
- `created_at`

Stores backtest runs and metrics.

### portfolios

- `id`
- `user_id`
- `name`
- `account_type`
- `cash_balance`
- `created_at`

Stores paper trading portfolios.

### paper_trades

- `id`
- `portfolio_id`
- `symbol_id`
- `side`
- `quantity`
- `price`
- `trade_time`
- `notes`

Stores simulated trades only.

### risk_events

- `id`
- `user_id`
- `portfolio_id`
- `symbol_id`
- `event_type`
- `severity`
- `message`
- `created_at`

Stores risk alerts and observations.

### subscriptions

- `id`
- `user_id`
- `plan`
- `status`
- `started_at`
- `ended_at`

Stores commercial plan status when SaaS is introduced.

## Security Notes

- Do not store broker credentials in current stages.
- Do not add live trading keys before compliance and security review.
- Keep paper trading separate from any future real trading module.
- Add audit logs before multi-user commercial use.
