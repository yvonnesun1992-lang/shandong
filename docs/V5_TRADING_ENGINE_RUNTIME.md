# V5.1 Trading Engine Runtime System

V5.1 turns the V5.0 paper trading components into a continuous runtime loop. It does not change the alpha model, factor logic, or strategy set.

## Runtime Heartbeat

The engine runs:

Market Data Tick -> Signal Engine -> Signal to Order -> Risk Check -> Execution Engine -> Portfolio Update -> PnL Update -> Log -> Next Tick

`runtime/trading_engine.py` owns the heartbeat and coordinates V5.0 paper trading modules.

## Runtime Modules

- `runtime/market_simulator.py`: replay-mode market open/close and synchronized tick feed.
- `runtime/event_bus.py`: event stream for MARKET_TICK, SIGNAL_GENERATED, ORDER_PLACED, ORDER_FILLED, POSITION_UPDATED, and RISK_TRIGGERED.
- `runtime/state_manager.py`: current positions, cash, active orders, open trades, and market regime state.
- `runtime/pnl_engine.py`: real-time equity curve, realized/unrealized PnL, and drawdown tracking.
- `runtime/risk_gate.py`: pre-trade checks, post-trade validation, and kill switch trigger.
- `runtime/monitor.py`: current equity, positions, PnL, signal flow rate, execution count, and latency.
- `runtime/system_controller.py`: start, stop, pause, resume, safe shutdown, and emergency stop controls.

## Safety Boundary

- No real broker connection.
- No real orders.
- No real account.
- No real capital.
- No payment system.
- No alpha model changes.
- No factor logic changes.
- No new strategy.

## Current Scope

This is a runtime system for paper trading and replay mode. Real-time adapters can be added later, but broker integration remains intentionally disabled.
