import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Evidence Sources', 'Summarizes V5.34 mock replay, V5.35 fault injection, and V5.36 stability gate evidence.', 'local summaries'],
  ['Completeness', 'Checks that replay, fault, redaction, schema, audit, order blocking, and safety evidence exists.', 'evidence only'],
  ['Redaction Pack', 'Documents placeholder-only account evidence and redacted balance and position values.', 'redacted'],
  ['Schema Pack', 'Documents placeholder schemas and malformed snapshot rejection evidence.', 'schema'],
  ['Audit Pack', 'Documents placeholder-only audit events and audit failure handling.', 'audit'],
  ['Order Blocking', 'Documents that preview, submission, and order intrusion paths remain blocked.', 'blocked'],
  ['Safety Boundary', 'Documents no sandbox API, no secrets, no account reads, no order path, and no funds path.', 'locked'],
];

export default function V5ReadOnlyEvidencePackPage() {
  return (
    <ProductionShell
      title="V5 Read-Only Evidence Pack"
      eyebrow="Sandbox Read-Only Connector Evidence Pack"
      description="Evidence pack only: consolidates local replay, fault, stability, schema, redaction, audit, order blocking, and safety evidence without enabling connector access."
      activePath="/v5-read-only-evidence-pack"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Evidence pack only" description="Local summaries and report material." />
        <MetricCard title="Decision" value="Evidence only" description="READ_ONLY_EVIDENCE_ONLY by design." />
        <MetricCard title="Connector Access" value="Disallowed" description="Completeness cannot unlock connector access." />
        <MetricCard title="Sandbox / Orders" value="Disabled" description="No API, account, balance, position, order, or money path." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Read-only evidence pack</h2>
          </div>
          <StatusBadge status="warning">Evidence only</StatusBadge>
        </div>
        <p className="muted">
          V5.37 packages local evidence from V5.34, V5.35, and V5.36. Evidence pack runtime, sandbox API, credential access, account reads, balance reads, position reads, order preview, order submission, broker connection, and real money remain disabled.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Pack</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="Evidence cannot unlock access"
        description="This page intentionally shows evidence packaging only. It does not connect to providers, read secrets, read accounts, read balances, read positions, preview orders, submit orders, or enable real funds."
      />
    </ProductionShell>
  );
}
