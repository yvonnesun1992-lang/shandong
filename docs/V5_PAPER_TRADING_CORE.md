# V5.0 Paper Trading Core System

V5.0 adds a paper trading simulation core. It is not a production deployment layer and it does not connect to a real broker, real account, payment system, or real-money execution path.

## Signal to Order Flow

The paper trading loop is:

Signal -> Order -> Execution -> Position -> Cash -> Portfolio Value -> PnL -> Risk Check -> Trade Log

`trading/signal_to_order.py` converts alpha-style signals into paper `Order` objects:

- `BUY` creates a buy order.
- `SELL` creates a sell order.
- `HOLD` returns no order.
- Quantity is based on account equity, signal strength, max order value, and max asset exposure.

## Paper Broker and Execution

`trading/paper_broker.py` connects the order model, execution engine, and paper account.

`trading/execution_engine.py` simulates market fills with fees, slippage, and rejection rules.

Default assumptions:

- `fee_rate = 0.001`
- `slippage_rate = 0.0005`

BUY execution:

- `execution_price = market_price * (1 + slippage_rate)`
- `cost = execution_price * quantity * (1 + fee_rate)`

SELL execution:

- `execution_price = market_price * (1 - slippage_rate)`
- `proceeds = execution_price * quantity * (1 - fee_rate)`

## Account and Portfolio Tracking

`trading/paper_account.py` tracks:

- initial cash
- cash
- positions
- realized PnL
- unrealized PnL
- equity
- trade history

Cash and positions are guarded so paper trades cannot silently create negative cash or negative positions.

## Risk Limits

`trading/risk_limits.py` enforces:

- max position per asset
- max order value
- max daily loss
- max drawdown

Default limits:

- single asset max: 20% of equity
- single order max: 10% of equity
- max drawdown: 10%
- max daily loss: 3%

## Paper Trading Runner

`trading/paper_trading_runner.py` runs the closed loop over historical or simulated market data:

- read current bar
- generate signal through an injected signal function
- convert signal to order
- run risk check
- execute paper order
- update market price
- record equity curve
- calculate performance metrics

## Performance Metrics

`trading/performance.py` calculates:

- total return
- annual return
- max drawdown
- Sharpe ratio
- win rate
- number of trades
- average trade return
- total fees
- total slippage cost

## Known Limitations

- This layer is paper trading only.
- It does not model exchange microstructure.
- It does not connect to broker APIs.
- It does not submit real orders.
- It does not manage real capital.
- It does not change the V5 alpha model or factor logic.

## Upgrade Path

The next safe upgrade is live paper trading with a market data adapter and persisted logs. Real broker integration should remain disabled until paper-trading behavior is validated for a sustained period with stable risk metrics.
