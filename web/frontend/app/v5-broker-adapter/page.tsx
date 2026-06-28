import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';
import {
  fetchV5BrokerAdapterCapabilities,
  fetchV5BrokerAdapterFactory,
  fetchV5BrokerAdapterList,
  fetchV5BrokerAdapterRegistry,
  fetchV5BrokerAdapterSafety,
} from '../lib/apiClient';

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export default async function V5BrokerAdapterPage() {
  const [listResult, capabilitiesResult, registryResult, factoryResult, safetyResult] = await Promise.all([
    fetchV5BrokerAdapterList(),
    fetchV5BrokerAdapterCapabilities(),
    fetchV5BrokerAdapterRegistry(),
    fetchV5BrokerAdapterFactory(),
    fetchV5BrokerAdapterSafety(),
  ]);
  const adapters = asList(listResult.data?.adapters);
  const capabilityMatrix = asRecord(capabilitiesResult.data?.capability_matrix);
  const registry = asRecord(registryResult.data?.registry);
  const compatibility = asRecord(registryResult.data?.compatibility);
  const factory = asRecord(factoryResult.data?.factory);
  const safety = asRecord(safetyResult.data?.safety);
  const summary = asRecord(safetyResult.data?.summary);
  const warnings = [...(listResult.warning ?? []), ...(safetyResult.warning ?? [])];

  return (
    <ProductionShell
      title="V5 Broker Adapter"
      eyebrow="Broker Adapter Skeleton + Sandbox Bridge"
      description="Skeleton-only adapter layer for future broker integrations. This stage is structure only."
      activePath="/v5-broker-adapter"
    >
      {!listResult.ok ? <ErrorState description={listResult.errorMessage ?? 'Backend unavailable. Showing safe skeleton state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Broker Adapter Registry" value={String(adapters.length || 6)} description="mock plus skeleton providers." status="OK" />
        <MetricCard title="Adapter Factory" value="skeleton only" description="no real connection" status="OK" />
        <MetricCard title="Safety Guard Status" value={String(safety.safe ?? true)} description="no real orders" status="OK" />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Safety Boundary</h2>
          <StatusBadge status="OK" />
        </div>
        <p>skeleton only</p>
        <p>no real connection</p>
        <p>no real orders</p>
        <p>paper trading only</p>
      </section>
      <div className="grid">
        <MetricCard title="Capability Matrix" value={String(Object.keys(capabilityMatrix).length || 6)} description="Mock supports simulated capabilities; skeleton providers are disabled." />
        <MetricCard title="Skeleton Adapters List" value={adapters.join(', ') || 'mock, ibkr_skeleton, alpaca_skeleton'} description="Future provider shapes only." />
        <MetricCard title="Compatibility Layer Check" value={String(compatibility.compatible ?? true)} description="V5.13 contract aligns with V5.14 mock surface." />
        <MetricCard title="Final Verdict" value={String(summary.verdict ?? 'PASS')} description="Adapter skeleton is safe for review." />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Registry and Factory</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ registry, factory }, null, 2)}</pre>
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Capability Matrix</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ capabilityMatrix, compatibility, safety }, null, 2)}</pre>
        </section>
      </div>
      {warnings.length ? <EmptyState title="Broker adapter skeleton warnings" description={warnings.join(' | ')} /> : null}
    </ProductionShell>
  );
}
