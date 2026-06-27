import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge, type StatusTone } from '../components/StatusBadge';
import { fetchV5LivePaperConfig, fetchV5LivePaperLatestTick, fetchV5LivePaperStatus, fetchV5LivePaperSummary } from '../lib/apiClient';

const fallbackStatus = {
  live_data_mode: 'mock_live',
  live_data_provider: 'mock',
  symbols: ['AAPL', 'MSFT', 'NVDA', 'SPY', 'QQQ'],
  live_market_data: true,
  paper_trading: true,
  real_trading: false,
  broker_connected: false,
  real_money_enabled: false,
};

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function tone(value: unknown): StatusTone {
  const text = String(value ?? '').toLowerCase();
  if (text.includes('fail') || text.includes('error')) return 'Error';
  if (text.includes('fallback') || text.includes('warning') || text.includes('degraded')) return 'Warning';
  return 'OK';
}

function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export default async function V5LivePaperPage() {
  const [statusResult, configResult, tickResult, summaryResult] = await Promise.all([
    fetchV5LivePaperStatus(),
    fetchV5LivePaperConfig(),
    fetchV5LivePaperLatestTick(),
    fetchV5LivePaperSummary(),
  ]);
  const status = {
    ...fallbackStatus,
    ...asRecord(asRecord(statusResult.data).live_paper),
  };
  const config = asRecord(configResult.data?.config ?? status);
  const latestTick = asRecord(tickResult.data?.latest_tick);
  const summary = asRecord(summaryResult.data?.summary);
  const portfolio = asRecord(summary.portfolio);
  const warnings = asList(summary.warnings);
  const errors = asList(summary.errors);
  const symbols = asList(status.symbols);

  return (
    <ProductionShell
      title="V5 Live Paper"
      eyebrow="Live Paper Trading Staging"
      description="Live market data staging for the V5 paper trading runtime. Market data may be live or fallback; execution remains simulated."
      activePath="/v5-live-paper"
    >
      {!statusResult.ok ? <ErrorState description={statusResult.errorMessage ?? 'Backend unavailable. Showing safe live paper fallback state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Live Paper Staging Status" value={String(summary.health_status ?? 'HEALTHY')} description="Live market data into paper trading loop." status={tone(summary.health_status)} />
        <MetricCard title="Live Data Provider" value={String(status.live_data_provider)} description="Live market data: enabled / fallback" status={tone(status.live_data_provider)} />
        <MetricCard title="Ticks Processed" value={String(summary.ticks_processed ?? 0)} description="Latest staging loop tick count." />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Safety Boundary</h2>
          <StatusBadge status="Warning" />
        </div>
        <p>Live market data: enabled / fallback</p>
        <p>Paper trading only</p>
        <p>Real trading: disabled</p>
        <p>Broker: not connected</p>
        <p>Real money: disabled</p>
      </section>
      <div className="grid">
        <MetricCard title="Mode" value={String(status.live_data_mode)} description="mock_live by default; yfinance polling is optional." />
        <MetricCard title="Symbols" value={String(symbols.length)} description={symbols.join(', ') || 'No symbols loaded'} />
        <MetricCard title="Paper Trading Status" value={status.paper_trading ? 'Enabled' : 'Review'} description="Paper-only runtime status." status={status.paper_trading ? 'OK' : 'Warning'} />
        <MetricCard title="Final Equity" value={String(summary.final_equity ?? portfolio.equity ?? 0)} description="Paper account equity only." />
        <MetricCard title="Risk Status" value={summary.risk_kill_switch_triggered ? 'Triggered' : 'Clear'} description="Risk gate status." status={summary.risk_kill_switch_triggered ? 'Error' : 'OK'} />
        <MetricCard title="Warnings / Errors" value={`${warnings.length} / ${errors.length}`} description="Live paper staging diagnostics." status={errors.length ? 'Error' : warnings.length ? 'Warning' : 'OK'} />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Latest Tick</h2>
            <StatusBadge status={latestTick.symbol ? 'OK' : 'Warning'} />
          </div>
          {latestTick.symbol ? <pre className="codeBlock">{JSON.stringify(latestTick, null, 2)}</pre> : <EmptyState title="No latest tick loaded" description="The page can render safely before market data is available." />}
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Health Status</h2>
            <StatusBadge status={tone(summary.health_status)} />
          </div>
          <pre className="codeBlock">{JSON.stringify({ config, summary: { mode: summary.mode, health_status: summary.health_status, warnings, errors } }, null, 2)}</pre>
        </section>
      </div>
    </ProductionShell>
  );
}
