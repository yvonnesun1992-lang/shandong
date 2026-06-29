import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Offline Replay Status', 'Offline replay only boundary and provider selection', 'replay runtime disabled'],
  ['Replay Scenario Catalog', 'Local placeholder replay scenario catalog', 'no external file reads'],
  ['Replay Loader', 'Loads generated local replay scenarios', 'no provider data reads'],
  ['Replay Runner', 'Advances placeholder replay states only', 'order submission disabled'],
  ['Consistency Validation', 'Event order, terminal state, idempotency, and audit checks', 'sandbox API disabled'],
  ['Failure Recovery', 'Timeout, rate limit, duplicate order, and recovery replay checks', 'no external retry call'],
  ['Audit Trail', 'Placeholder audit events with redacted provider payload markers', 'raw payload stored false'],
  ['Safety Validation', 'SDK, credential, network, account, order, and endpoint boundaries', 'broker connected false'],
  ['Final Summary', 'Offline replay verdict and warnings', 'paper trading only'],
];

export default function V5ProviderOfflineReplayPage() {
  return (
    <ProductionShell
      title="V5 Offline Replay"
      eyebrow="Provider Sandbox Connector Offline Replay Harness"
      description="Offline replay validation for mock connector event sequencing, failure recovery, idempotency, audit consistency, and safety boundaries."
      activePath="/v5-provider-offline-replay"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Offline replay only" description="Replay runtime disabled." />
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
          Offline replay only. Replay runtime disabled. Sandbox API disabled. Account read disabled. Order submission disabled. Broker connected false. Real money disabled. Paper trading only.
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
        description="This page intentionally shows offline replay state only. It does not connect to sandbox APIs, read accounts, create keys, store raw provider payloads, or submit orders."
      />
    </ProductionShell>
  );
}
