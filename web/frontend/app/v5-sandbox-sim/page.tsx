import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';
import {
  fetchV5SandboxSimAccount,
  fetchV5SandboxSimFills,
  fetchV5SandboxSimOrders,
  fetchV5SandboxSimScenarios,
  fetchV5SandboxSimStatus,
  fetchV5SandboxSimSummary,
} from '../lib/apiClient';

const fallback = {
  local_simulation: true,
  real_sandbox_api_enabled: false,
  broker_connected: false,
  real_orders_enabled: false,
  real_money_enabled: false,
  paper_trading: true,
  simulation_only: true,
};

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export default async function V5SandboxSimPage() {
  const [statusResult, accountResult, ordersResult, fillsResult, scenariosResult, summaryResult] = await Promise.all([
    fetchV5SandboxSimStatus(),
    fetchV5SandboxSimAccount(),
    fetchV5SandboxSimOrders(),
    fetchV5SandboxSimFills(),
    fetchV5SandboxSimScenarios(),
    fetchV5SandboxSimSummary(),
  ]);
  const status = { ...fallback, ...asRecord(asRecord(statusResult.data).sandbox_simulation) };
  const account = asRecord(accountResult.data?.account);
  const orders = asList(ordersResult.data?.orders);
  const fills = asList(fillsResult.data?.fills);
  const scenarios = asList(scenariosResult.data?.scenarios);
  const summary = asRecord(asRecord(summaryResult.data).sandbox_simulation);
  const runSummary = asRecord(summary.summary);
  const warnings = [...(statusResult.warning ?? []), ...(ordersResult.warning ?? []), ...(summaryResult.warning ?? [])];

  return (
    <ProductionShell
      title="V5 Sandbox Sim"
      eyebrow="Sandbox Simulation Harness"
      description="Local-only broker sandbox simulation for order lifecycle rehearsal. No sandbox API connection is enabled."
      activePath="/v5-sandbox-sim"
    >
      {!statusResult.ok ? <ErrorState description={statusResult.errorMessage ?? 'Backend unavailable. Showing safe local simulation fallback state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Sandbox Simulation Status" value="Local simulation only" description="Sandbox API: disabled" status="OK" />
        <MetricCard title="Broker Boundary" value="Disconnected" description="Broker connected: false" status="OK" />
        <MetricCard title="Order Boundary" value="Simulated" description="Real orders: disabled" status="OK" />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Safety Boundary</h2>
          <StatusBadge status="OK" />
        </div>
        <p>Local simulation only</p>
        <p>Sandbox API: disabled</p>
        <p>Broker connected: false</p>
        <p>Real orders: disabled</p>
        <p>Real money: disabled</p>
        <p>Paper trading only</p>
      </section>
      <div className="grid">
        <MetricCard title="Simulation Scenario" value={String(runSummary.scenario ?? 'full_fill')} description={`${scenarios.length || 9} local scenarios available.`} />
        <MetricCard title="Simulated Account" value={String(account.equity ?? '100000')} description="Local cash, positions, and equity only." />
        <MetricCard title="Simulated Orders" value={String(orders.length)} description="Orders are local simulated orders." />
        <MetricCard title="Simulated Fills" value={String(fills.length)} description="Fill records are local simulated fills." />
        <MetricCard title="Fault Simulation" value="Available" description="Disconnect, latency, stale price, and partial fill cases." status="Warning" />
        <MetricCard title="Final Verdict" value={String(summary.verdict ?? 'PASS')} description="Simulation readiness report state." />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Lifecycle Summary</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ status, account, orders, fills }, null, 2)}</pre>
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Scenario Summary</h2>
            <StatusBadge status="Warning" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ scenarios, summary }, null, 2)}</pre>
        </section>
      </div>
      {warnings.length ? <EmptyState title="Sandbox simulation warnings" description={warnings.join(' | ')} /> : null}
    </ProductionShell>
  );
}
