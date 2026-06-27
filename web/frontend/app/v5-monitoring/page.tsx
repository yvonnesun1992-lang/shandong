import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge, type StatusTone } from '../components/StatusBadge';
import {
  fetchV5MonitoringErrors,
  fetchV5MonitoringHealth,
  fetchV5MonitoringPnl,
  fetchV5MonitoringPositions,
  fetchV5MonitoringRisk,
  fetchV5MonitoringSignals,
  fetchV5MonitoringSoakReport,
  fetchV5MonitoringSummary,
  fetchV5MonitoringTrades,
} from '../lib/apiClient';

const fallbackSummary = {
  status: 'UNKNOWN',
  mode: 'UNKNOWN',
  paper_trading: true,
  real_trading: false,
  broker_connected: false,
  latest_equity: 0,
  cash: 0,
  position_value: 0,
  open_positions: [],
  recent_signals: [],
  recent_trades: [],
  recent_errors: [],
  health: {},
  risk: {},
  soak_report: { status: 'UNKNOWN', summary: '' },
};

function tone(value: unknown): StatusTone {
  const text = String(value ?? '').toLowerCase();
  if (text.includes('fail') || text.includes('error')) return 'Error';
  if (text.includes('degraded') || text.includes('warning') || text.includes('safe')) return 'Warning';
  return 'OK';
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function listCount(value: unknown) {
  return Array.isArray(value) ? value.length : 0;
}

export default async function V5MonitoringPage() {
  const [summaryResult, pnlResult, positionsResult, signalsResult, tradesResult, errorsResult, healthResult, riskResult, soakResult] =
    await Promise.all([
      fetchV5MonitoringSummary(),
      fetchV5MonitoringPnl(),
      fetchV5MonitoringPositions(),
      fetchV5MonitoringSignals(),
      fetchV5MonitoringTrades(),
      fetchV5MonitoringErrors(),
      fetchV5MonitoringHealth(),
      fetchV5MonitoringRisk(),
      fetchV5MonitoringSoakReport(),
    ]);
  const summary = {
    ...fallbackSummary,
    ...asRecord(asRecord(summaryResult.data).monitoring),
  };
  const pnl = asRecord(asRecord(pnlResult.data).pnl);
  const positions = (positionsResult.data?.positions as unknown[]) ?? summary.open_positions;
  const signals = (signalsResult.data?.signals as unknown[]) ?? summary.recent_signals;
  const trades = (tradesResult.data?.trades as unknown[]) ?? summary.recent_trades;
  const errors = (errorsResult.data?.errors as unknown[]) ?? summary.recent_errors;
  const health = asRecord(healthResult.data?.health ?? summary.health);
  const risk = asRecord(riskResult.data?.risk ?? summary.risk);
  const soakReport = asRecord(soakResult.data?.soak_report ?? summary.soak_report);
  const hasBackend = summaryResult.ok;

  return (
    <ProductionShell
      title="V5 Monitoring"
      eyebrow="Live Paper Trading"
      description="Dashboard-ready visibility for V5 runtime logs, checkpoints, soak test reports, PnL, risk, and health."
      activePath="/v5-monitoring"
    >
      {!hasBackend ? <ErrorState description={summaryResult.errorMessage ?? 'Backend unavailable. Showing safe fallback monitoring state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="System Status" value={String(summary.status)} description="Runtime health from checkpoint and monitoring data." status={tone(summary.status)} />
        <MetricCard title="Mode" value={String(summary.mode)} description="NORMAL / DEGRADED / SAFE_MODE visibility." status={tone(summary.mode)} />
        <MetricCard title="Latest Equity" value={String(pnl.latest_equity ?? summary.latest_equity)} description="Paper account equity only." />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Paper Trading Safety Boundary</h2>
          <StatusBadge status="Warning" />
        </div>
        <p>Paper trading only</p>
        <p>No real broker connected</p>
        <p>No real orders</p>
        <p>No real capital</p>
        <p>No production deployment</p>
      </section>
      <div className="grid">
        <MetricCard title="Cash" value={String(pnl.cash ?? summary.cash)} description="Latest checkpoint cash." />
        <MetricCard title="Position Value" value={String(pnl.position_value ?? summary.position_value)} description="Marked paper position value." />
        <MetricCard title="Positions" value={String(listCount(positions))} description="Open paper positions." />
        <MetricCard title="Recent Signals" value={String(listCount(signals))} description="Latest signal events." />
        <MetricCard title="Recent Trades" value={String(listCount(trades))} description="Latest paper fill events." />
        <MetricCard title="Recent Errors" value={String(listCount(errors))} description="Latest runtime errors." status={listCount(errors) > 0 ? 'Warning' : 'OK'} />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Risk Status</h2>
            <StatusBadge status={tone(summary.mode)} />
          </div>
          <pre className="codeBlock">{JSON.stringify(risk, null, 2)}</pre>
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Health Status</h2>
            <StatusBadge status={tone(health.status ?? summary.status)} />
          </div>
          <pre className="codeBlock">{JSON.stringify(health, null, 2)}</pre>
        </section>
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Soak Test Report Summary</h2>
          <StatusBadge status={tone(soakReport.status)} />
        </div>
        {soakReport.summary ? <pre className="codeBlock">{String(soakReport.summary).slice(0, 1200)}</pre> : <EmptyState title="No soak report loaded" description="The monitoring layer can run safely without local report files." />}
      </section>
    </ProductionShell>
  );
}
