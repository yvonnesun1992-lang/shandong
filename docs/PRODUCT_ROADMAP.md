# Product Roadmap

shandong is evolving from a personal quantitative research tool into a stock quantitative research, paper trading, and analytics platform.

The product must grow in stages. Each stage should keep the compliance boundary clear: research, historical backtesting, risk observation, and simulated trading only until formal compliance review allows anything more.

## V1: Personal Quant Research System

### Goal

Build a beginner-friendly local research system for A-share and US stock trend analysis.

### Features

- User-defined watchlists.
- OHLCV data loading.
- MA20, MA60, MA120, RSI14, and volume MA20.
- Trend score from 0 to 100.
- Simple single-stock backtest.
- Streamlit dashboard.

### Not Doing

- No real brokerage connection.
- No live trading.
- No automatic order placement.
- No paid user system.
- No investment advice.

### Risks

- Public data source instability.
- Beginner users may confuse backtest output with future returns.
- Simple backtest does not include all real-world trading frictions.

### Acceptance Criteria

- Local install succeeds.
- Tests pass.
- Dashboard opens locally.
- User can view trend scores, charts, and simple backtest results or clear data-source errors.

## V1.1: Data Fallback And Caching

### Goal

Improve local reliability when yfinance or AkShare fails.

### Features

- Local sample OHLCV data.
- Data fallback when external sources fail.
- Streamlit data caching.
- Clear sample-data warning in dashboard.
- Tests for sample data, indicators, and backtest compatibility.

### Not Doing

- No paid data vendor integration.
- No database migration.
- No user accounts.
- No real-time trading.

### Risks

- Users may mistake sample data for real market data.
- Cache freshness needs clear communication.
- Fallback must not silently produce investment conclusions.

### Acceptance Criteria

- Dashboard can demonstrate ranking, charting, and backtest without network.
- Sample data is clearly marked.
- Tests pass.

## V1.2: Dashboard Experience Optimization

### Goal

Make the local dashboard easier for non-technical users to understand.

### Features

- Clearer data-source status.
- Better loading states.
- Better error messages.
- Basic report export.
- More readable chart layout.

### Not Doing

- No commercial subscriptions.
- No user login.
- No live trading.
- No personalized investment recommendation.

### Risks

- Better UI may make results look more authoritative than they are.
- Exported reports need disclaimers.

### Acceptance Criteria

- Users can understand whether data is real, cached, or sample.
- Dashboard remains stable when a data source fails.
- All exported or displayed outputs include research-only positioning.

## V2: Multi-User Quant Research Platform

### Goal

Support multiple users managing watchlists, strategies, and backtests.

### Features

- User accounts.
- Saved watchlists.
- Saved strategy configurations.
- Backtest history.
- Basic risk dashboards.
- Server-side data cache.

### Not Doing

- No real brokerage connection.
- No automatic order placement.
- No paid trading signals.
- No managed accounts.

### Risks

- User data privacy.
- Data licensing and redistribution.
- Strategy results may be interpreted as advice.

### Acceptance Criteria

- Multiple users can manage independent watchlists and backtests.
- User data is separated.
- Platform disclaimers are visible.
- No real trading capability exists.

## V2.5: Paper Trading

### Goal

Let users simulate portfolios and trades without real money.

### Features

- Simulated cash accounts.
- Paper buy and sell records.
- Portfolio P&L.
- Risk events.
- Trade journal.
- Strategy-to-paper-trade simulation.

### Not Doing

- No real broker API.
- No real order routing.
- No margin, leverage, or derivatives trading in early versions.
- No guarantee of execution realism.

### Risks

- Users may overtrust simulated performance.
- Paper trading fills may differ from real market execution.
- Need strict labeling as simulation.

### Acceptance Criteria

- Every simulated trade is clearly labeled as paper trading.
- No real money movement exists.
- No broker credential collection exists.

## V3: SaaS Commercial Platform

### Goal

Offer a subscription-based research and simulation platform.

### Features

- Subscription plans.
- More watchlists.
- More backtest capacity.
- Report export.
- Team accounts.
- API access for research data.
- Private deployment option.

### Not Doing

- No paid individualized investment advice.
- No automated real-money trading.
- No performance guarantees.
- No use of unlicensed data redistribution.

### Risks

- Securities advisory rules.
- Data vendor licensing.
- Marketing claims.
- Payment and privacy compliance.

### Acceptance Criteria

- Commercial copy stays research-tool focused.
- Subscription features do not become paid buy/sell recommendations.
- Legal and compliance review is completed before public launch.

## V4: Real Brokerage Interface / Live Trading

### Goal

Consider real brokerage connectivity only after compliance review.

### Features

- To be defined after legal, regulatory, broker, security, and risk review.

### Not Doing Until Approved

- No real broker connection.
- No order placement.
- No automatic trading.
- No broker credential storage.
- No trading signal execution.

### Risks

- Securities regulation.
- Broker API terms.
- Programmatic trading rules.
- Cybersecurity and credential storage.
- User suitability and risk disclosure.

### Acceptance Criteria

- Formal compliance review completed.
- Legal requirements understood for target jurisdictions.
- Broker terms reviewed.
- Security architecture reviewed.
- Explicit user consent and risk controls designed.
