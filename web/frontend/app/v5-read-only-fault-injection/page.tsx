import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Redaction Failure', 'Detects account refs, numeric balances, quantities, values, and placeholder key faults.', 'blocked'],
  ['Malformed Payloads', 'Validates malformed account, balance, position, and unknown provider snapshots.', 'detected'],
  ['Stale Snapshot', 'Flags expired timestamp placeholders and market session mismatch placeholders.', 'detected'],
  ['Audit Failure', 'Simulates audit write failure and requires fallback without raw value logging.', 'fallback'],
  ['Rate Limit', 'Simulates read-only rate limit faults without network retry.', 'circuit breaker'],
  ['Order Intrusion', 'Blocks preview, submission, order identifiers, and trade intent fields.', 'blocked'],
];

export default function V5ReadOnlyFaultInjectionPage() {
  return (
    <ProductionShell
      title="V5 Read-Only Fault Injection"
      eyebrow="Sandbox Read-Only Connector Fault Injection"
      description="Fault injection only: local mock fault payloads validate redaction, stale snapshots, malformed payloads, audit failures, rate limits, and order path intrusion without provider access."
      activePath="/v5-read-only-fault-injection"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Fault injection only" description="Local mock fault cases without runtime connector." />
        <MetricCard title="Sandbox API" value="Disabled" description="No provider endpoint or external network access." />
        <MetricCard title="Fault Cases" value="Blocked" description="All injected faults must be rejected or warned." />
        <MetricCard title="Orders / Money" value="Disabled" description="No preview, submission, broker, or funds path." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Read-only fault injection</h2>
          </div>
          <StatusBadge status="warning">Local only</StatusBadge>
        </div>
        <p className="muted">
          V5.35 validates failure handling for local mock payloads only. Runtime connector, sandbox API, credential access, account reads, balance reads, position reads, order preview, order submission, broker connection, and real money remain disabled.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Fault</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="No live connector"
        description="This page intentionally shows local fault injection only. It does not connect to providers, read accounts, read balances, read positions, preview orders, submit orders, or enable real funds."
      />
    </ProductionShell>
  );
}
