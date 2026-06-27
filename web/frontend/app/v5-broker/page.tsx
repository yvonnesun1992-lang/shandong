import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge, type StatusTone } from '../components/StatusBadge';
import { fetchV5BrokerOrderMapping, fetchV5BrokerReadiness, fetchV5BrokerSafety, fetchV5BrokerStatus } from '../lib/apiClient';

const fallback = {
  broker_connected: false,
  real_orders_enabled: false,
  real_money_enabled: false,
  paper_trading: true,
  planning_only: true,
  broker_provider: 'none',
  broker_execution_mode: 'paper_only',
};

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function tone(value: unknown): StatusTone {
  const text = String(value ?? '').toLowerCase();
  if (text.includes('fail') || text.includes('error')) return 'Error';
  if (text.includes('warning') || text.includes('not_ready') || text.includes('planning')) return 'Warning';
  return 'OK';
}

export default async function V5BrokerPage() {
  const [statusResult, readinessResult, safetyResult, mappingResult] = await Promise.all([
    fetchV5BrokerStatus(),
    fetchV5BrokerReadiness(),
    fetchV5BrokerSafety(),
    fetchV5BrokerOrderMapping(),
  ]);
  const status = { ...fallback, ...asRecord(asRecord(statusResult.data).broker) };
  const readiness = asRecord(readinessResult.data?.readiness);
  const safety = asRecord(safetyResult.data?.safety);
  const mapping = asRecord(mappingResult.data?.order_mapping);
  const missing = asList(readiness.missing_production_requirements);
  const warnings = [...(statusResult.warning ?? []), ...(readinessResult.warning ?? []), ...(safetyResult.warning ?? []), ...(mappingResult.warning ?? [])];

  return (
    <ProductionShell
      title="V5 Broker"
      eyebrow="Broker Integration Planning"
      description="Planning-only broker adapter, safety gate, and mapping readiness. No external broker connection is active."
      activePath="/v5-broker"
    >
      {!statusResult.ok ? <ErrorState description={statusResult.errorMessage ?? 'Backend unavailable. Showing safe broker planning fallback state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Broker Integration Status" value="Planning only" description="Broker connected: false" status="Warning" />
        <MetricCard title="Execution Mode" value={String(status.broker_execution_mode ?? 'paper_only')} description="Real orders: disabled" />
        <MetricCard title="Capital Boundary" value="Disabled" description="Real money: disabled" status="OK" />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Safety Boundary</h2>
          <StatusBadge status="Warning" />
        </div>
        <p>Broker connected: false</p>
        <p>Real orders: disabled</p>
        <p>Real money: disabled</p>
        <p>Paper trading only</p>
        <p>Planning only</p>
      </section>
      <div className="grid">
        <MetricCard title="Planned Provider" value={String(status.broker_provider ?? 'none')} description="Provider plan only, no SDK loaded." />
        <MetricCard title="Adapter Interface" value="Defined" description="Default behavior rejects external broker actions." status="OK" />
        <MetricCard title="Order Mapping Plan" value={String(mapping.mapping_ready ?? false)} description="Mapping documentation only." status={tone(mapping.mapping_ready)} />
        <MetricCard title="Required Safety Gates" value={String(asList(safety.checks).length || 6)} description="Manual approval, kill switch, and position limits planned." />
        <MetricCard title="Missing Production Requirements" value={String(missing.length || 6)} description="Items required before any future broker work." status="Warning" />
        <MetricCard title="Final Verdict" value={String(readiness.verdict ?? 'WARNING')} description="Planning readiness report status." status={tone(readiness.verdict)} />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Broker Adapter Interface</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ status, safety }, null, 2)}</pre>
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Order Mapping Plan</h2>
            <StatusBadge status="Warning" />
          </div>
          {Object.keys(mapping).length ? <pre className="codeBlock">{JSON.stringify(mapping, null, 2)}</pre> : <EmptyState title="No mapping payload loaded" description="The page can render safely before the backend is available." />}
        </section>
      </div>
      {warnings.length ? <EmptyState title="Broker planning warnings" description={warnings.join(' | ')} /> : null}
    </ProductionShell>
  );
}
