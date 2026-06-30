import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Sandbox Evidence Status', 'Evidence-only boundary and provider selection', 'evidence runtime disabled'],
  ['Evidence Sources', 'Local V5.23, V5.24, and V5.25 report presence', 'local files only'],
  ['Replay Evidence', 'Offline replay scenarios, timeout recovery, duplicate replay, rate limit replay, audit, and safety evidence', 'no provider calls'],
  ['Fault Evidence', 'Fault detection, recovery, kill switch, idempotency, audit, and safety evidence', 'sandbox API disabled'],
  ['Soak Evidence', 'Soak scenarios, stability metrics, gate, coverage, safety, audit, and error budget evidence', 'order submission disabled'],
  ['Readiness Gaps', 'Credential vault, account approval, permission, legal, operator, kill switch, audit, and endpoint gaps', 'blocked'],
  ['Sandbox Entry Gate', 'Sandbox API and sandbox orders remain blocked', 'broker connected false'],
  ['Safety Validation', 'SDK, credential, network, account, order, payload, and endpoint boundaries', 'real money disabled'],
  ['Final Summary', 'Evidence pack verdict and readiness state', 'paper trading only'],
];

export default function V5SandboxEvidencePage() {
  return (
    <ProductionShell
      title="V5 Sandbox Evidence"
      eyebrow="Provider Sandbox Readiness Evidence Pack"
      description="Evidence-only readiness pack for future sandbox preparation, based on offline replay, fault injection, and offline soak reports."
      activePath="/v5-sandbox-evidence"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Evidence only" description="Evidence runtime disabled." />
        <MetricCard title="Sandbox Entry" value="Blocked" description="Sandbox API and sandbox orders remain blocked." />
        <MetricCard title="Account Read" value="Disabled" description="Account read disabled; local evidence only." />
        <MetricCard title="Order Submission" value="Disabled" description="Order submission disabled and broker connected false." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Sandbox entry blocked</h2>
          </div>
          <StatusBadge status="warning">Evidence only</StatusBadge>
        </div>
        <p className="muted">
          Evidence pack only. Sandbox API disabled. Account read disabled. Order submission disabled. Broker connected false. Real money disabled. Paper trading only.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Blocked</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="No sandbox runtime"
        description="This page intentionally shows evidence state only. It does not connect to sandbox APIs, read accounts, create credentials, store raw provider payloads, or submit orders."
      />
    </ProductionShell>
  );
}
