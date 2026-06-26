# V1.1 Quant Alpha Backtest Report

## Scope

This report validates the V1.1 paper trading research loop:

Data -> Feature Engine -> Regime Detection -> Strategy Ensemble -> Risk Engine -> Paper Broker -> Backtest Report.

The run is a deterministic local sample for system verification. It is not financial advice, not a live trading signal, and not connected to any broker.

## Sample Setup

- Symbol: AAPL
- Initial cash: 100000
- Strategy: StrategyEnsemble
- Trade fraction: 20%
- Fee: 0.1%
- Slippage: 0.05%
- Data: deterministic synthetic OHLCV sample

## Metrics

- Total return: 5.86%
- Annual return: 9.39%
- Max drawdown: 0.01%
- Sharpe ratio: 28.31
- Sortino ratio: 0.00
- Calmar ratio: 629.37
- Risk-adjusted return: 5.86%
- Number of trades: 1

## Regime Breakdown

- Bull: primary performance regime in the sample path
- Sideways: early warm-up and neutral periods
- Bear: not present in this upward deterministic sample

## Strategy Contribution

- Momentum contributed the strongest positive vote in the sample
- MA crossover contributed positive trend confirmation
- Mean reversion contributed mild negative pressure during extended trend periods
- Volatility breakout remained neutral in the sample

## Risk Controls

- Max position per asset control is active
- Drawdown control is active
- Volatility deleveraging is active
- Risk score is recorded on each equity row

## Safety Boundary

- No broker API
- No real trading
- No auto order routing
- No real account
- No external AI API
- No external payment or real-money execution
