import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Controlled Enablement Conditions', 'Future requirements for moving from NO-GO to controlled GO.', 'not met'],
  ['Staged Unlock Plan', 'Eight non-executable stages from plan-only through future blocked order submission review.', 'disabled'],
  ['Feature Flags', 'Dependency graph for controlled GO, credential read, sandbox API, account read, order preview, and blockers.', 'blocked'],
  ['Credential Read', 'Future vault, scope, operator approval, audit, and revocation requirements.', 'disabled'],
  ['Sandbox API', 'Future sandbox connectivity prerequisites without any current network path.', 'disabled'],
  ['Account Read', 'Future read-only checks with redaction and rate guard requirements.', 'disabled'],
  ['Order Preview', 'Future preview-only design that cannot submit orders.', 'disabled'],
  ['Emergency Stop', 'Stop conditions for leakage, unexpected responses, audit failure, rollback failure, or operator cancellation.', 'no runtime'],
];

export default function V5ControlledEnablementPage() {
  return (
    <ProductionShell
      title="V5 Controlled Enablement"
      eyebrow="Sandbox Dry-Run Controlled Enablement Blueprint"
      description="Blueprint for a future controlled dry-run path, with runtime, sandbox API, credential read, account read, order preview, and order submission locked."
      activePath="/v5-controlled-enablement"
    >
      <section className="grid">
        <MetricCard title="Decision" value="CONTROLLED_GO_BLOCKED" description="Controlled GO cannot be enabled in V5.32." />
        <MetricCard title="Runtime" value="Disabled" description="No controlled enablement runtime." />
        <MetricCard title="Sandbox / Credential / Account" value="Disabled" description="No sandbox API, credential read, or account read." />
        <MetricCard title="Orders / Money" value="Disabled" description="No order preview, order submission, or real money." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Controlled blueprint only</h2>
          </div>
          <StatusBadge status="warning">Blocked</StatusBadge>
        </div>
        <p className="muted">
          V5.32 documents future controlled enablement conditions only. Controlled GO, sandbox API, credential read, account read, order preview, order submission, broker connection, and real money are disabled.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Blueprint</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="No controlled launch"
        description="This page intentionally shows a future enablement blueprint only. It does not connect to a broker, read credentials, read accounts, preview orders, submit orders, or enable real money."
      />
    </ProductionShell>
  );
}
