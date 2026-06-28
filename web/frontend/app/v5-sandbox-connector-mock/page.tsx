import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';
import {
  fetchV5SandboxConnectorMockAccount,
  fetchV5SandboxConnectorMockPositions,
  fetchV5SandboxConnectorMockRecentOrders,
  fetchV5SandboxConnectorMockSafety,
  fetchV5SandboxConnectorMockScenarios,
  fetchV5SandboxConnectorMockStatus,
  fetchV5SandboxConnectorMockSummary,
} from '../lib/apiClient';

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function compact(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

export default async function V5SandboxConnectorMockPage() {
  const [statusResult, accountResult, positionsResult, ordersResult, scenariosResult, safetyResult, summaryResult] = await Promise.all([
    fetchV5SandboxConnectorMockStatus(),
    fetchV5SandboxConnectorMockAccount(),
    fetchV5SandboxConnectorMockPositions(),
    fetchV5SandboxConnectorMockRecentOrders(),
    fetchV5SandboxConnectorMockScenarios(),
    fetchV5SandboxConnectorMockSafety(),
    fetchV5SandboxConnectorMockSummary(),
  ]);
  const status = asRecord(statusResult.data?.sandbox_connector_mock);
  const account = asRecord(accountResult.data?.account);
  const positions = asRecord(positionsResult.data?.positions);
  const orders = asRecord(ordersResult.data?.recent_orders);
  const scenarios = asRecord(scenariosResult.data?.scenarios);
  const safety = asRecord(safetyResult.data?.safety);
  const summary = asRecord(summaryResult.data?.summary);
  const warnings = [...(statusResult.warning ?? []), ...(summaryResult.warning ?? [])];

  return (
    <ProductionShell
      title="V5 Sandbox Connector Mock"
      eyebrow="Sandbox Connector Mock Implementation"
      description="Local mock connector surface for connector contract demos and integration checks."
      activePath="/v5-sandbox-connector-mock"
    >
      {!statusResult.ok ? <ErrorState description={statusResult.errorMessage ?? 'Backend unavailable. Showing safe mock fallback state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Sandbox Connector Mock Status" value="Mock connector only" description="Connector runtime: disabled" status="OK" />
        <MetricCard title="Sandbox API" value="Disabled" description="Sandbox API: disabled" status="OK" />
        <MetricCard title="Trading Boundary" value="Paper trading only" description="Real orders: disabled" status="OK" />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Safety Boundary</h2>
          <StatusBadge status="OK" />
        </div>
        <p>Mock connector only</p>
        <p>Connector runtime: disabled</p>
        <p>Sandbox API: disabled</p>
        <p>Broker connected: false</p>
        <p>Real orders: disabled</p>
        <p>Real money: disabled</p>
        <p>Paper trading only</p>
      </section>
      <div className="grid">
        <MetricCard title="Account" value={String(account.account_mode ?? 'local_mock')} description="Local account fixture." />
        <MetricCard title="Positions" value={String(positions.positions_count ?? 0)} description="Mock position list." />
        <MetricCard title="Recent Orders" value={String(orders.order_count ?? 0)} description="Mock lifecycle records." />
        <MetricCard title="Scenario Count" value={String(asRecord(scenarios.summary).scenario_count ?? 12)} description="Accepted, fill, reject, duplicate, timeout, and risk cases." />
        <MetricCard title="Safety" value={String(safety.safe ?? true)} description="Output sanitized and local only." />
        <MetricCard title="Verdict" value={String(summary.verdict ?? 'PASS')} description="Mock connector check result." />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Mock Connector Status</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{compact({ status, account, positions })}</pre>
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Scenario Results</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{compact({ scenarios, safety, summary })}</pre>
        </section>
      </div>
      {warnings.length ? <EmptyState title="Mock connector warnings" description={warnings.join(' | ')} /> : null}
    </ProductionShell>
  );
}
