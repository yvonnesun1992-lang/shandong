import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Replay Evidence', 'Aggregates V5.34 mock replay evidence without enabling connector access.', 'evidence'],
  ['Fault Evidence', 'Aggregates V5.35 blocked fault injection evidence.', 'blocked'],
  ['Redaction Stability', 'Confirms redacted mock values and detected unredacted fault payloads.', 'stable'],
  ['Schema Stability', 'Confirms placeholder schemas and malformed payload rejection.', 'stable'],
  ['Audit Stability', 'Confirms audit fallback and no raw value logging.', 'stable'],
  ['Order Path Stability', 'Confirms order preview and submission paths remain blocked.', 'blocked'],
];

export default function V5ReadOnlyStabilityGatePage() {
  return (
    <ProductionShell
      title="V5 Read-Only Stability Gate"
      eyebrow="Sandbox Read-Only Connector Stability Gate"
      description="Stability gate only: aggregates replay and fault evidence, but keeps the decision blocked and every real connector path disabled."
      activePath="/v5-read-only-stability-gate"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Stability gate only" description="Evidence aggregation without runtime connector." />
        <MetricCard title="Decision" value="Blocked" description="STABILITY_GATE_BLOCKED by design." />
        <MetricCard title="Connector Access" value="Disallowed" description="Passing evidence cannot unlock read-only connector access." />
        <MetricCard title="Orders / Money" value="Disabled" description="No preview, submission, broker, or funds path." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Read-only stability gate</h2>
          </div>
          <StatusBadge status="warning">Blocked</StatusBadge>
        </div>
        <p className="muted">
          V5.36 summarizes V5.34 replay evidence and V5.35 fault evidence. Stability gate runtime, sandbox API, credential access, account reads, balance reads, position reads, order preview, order submission, broker connection, and real money remain disabled.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Gate</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="Gate remains blocked"
        description="This page intentionally shows evidence readiness only. It does not connect to providers, read accounts, read balances, read positions, preview orders, submit orders, or enable real funds."
      />
    </ProductionShell>
  );
}
