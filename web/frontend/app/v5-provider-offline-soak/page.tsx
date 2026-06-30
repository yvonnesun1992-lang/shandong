import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Offline Soak Status', 'Offline soak boundary and provider selection', 'soak runtime disabled'],
  ['Scenario Plan', 'Short, medium, long, mixed, duplicate, rate limit, timeout, audit, state, and safety soak scenarios', 'local plan only'],
  ['Event Generator', 'Deterministic placeholder event generation', 'no provider calls'],
  ['Soak Runner', 'Processes offline replay and fault events', 'order submission disabled'],
  ['Stability Metrics', 'Processed event ratio, warning rate, error rate, audit coverage, duplicate detection, and stability score', 'sandbox API disabled'],
  ['Stability Gate', 'Blocks unsafe soak outcomes and enforces audit/error/safety thresholds', 'broker connected false'],
  ['Coverage Validation', 'Checks replay, fault, timeout, duplicate, rate limit, rejection, partial fill, audit, recovery, and safety coverage', 'offline only'],
  ['Safety Validation', 'SDK, credential, network, account, order, payload, and endpoint boundaries', 'real money disabled'],
  ['Final Summary', 'Offline soak verdict and readiness gate status', 'paper trading only'],
];

export default function V5ProviderOfflineSoakPage() {
  return (
    <ProductionShell
      title="V5 Offline Soak"
      eyebrow="Provider Sandbox Offline Soak & Stability Gate"
      description="Offline long-run stability validation for replay, fault recovery, idempotency, state machine, audit, and safety boundary behavior."
      activePath="/v5-provider-offline-soak"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Offline soak only" description="Soak runtime disabled." />
        <MetricCard title="Sandbox API" value="Disabled" description="Sandbox API disabled and no network calls are made." />
        <MetricCard title="Account Read" value="Disabled" description="Account read disabled; placeholders only." />
        <MetricCard title="Order Submission" value="Disabled" description="Order submission disabled and broker connected false." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Paper trading only</h2>
          </div>
          <StatusBadge status="warning">Offline</StatusBadge>
        </div>
        <p className="muted">
          Offline soak only. Soak runtime disabled. Sandbox API disabled. Account read disabled. Order submission disabled. Broker connected false. Real money disabled. Paper trading only.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Offline</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="No provider runtime"
        description="This page intentionally shows offline soak state only. It does not connect to sandbox APIs, read accounts, create credentials, store raw provider payloads, or submit orders."
      />
    </ProductionShell>
  );
}
