import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Pre-Sandbox Approval Status', 'Approval gate-only status with all real paths disabled.', 'approval runtime disabled'],
  ['Approval Request Schema', 'Future request fields represented by placeholders only.', 'placeholder approval id'],
  ['Evidence Requirements', 'Evidence pack, vault design, connector design, replay, fault, and soak requirements.', 'entry gate blocked'],
  ['Operator Roles', 'Strategy, risk, technical, compliance, and emergency operator policy.', 'all approvals disabled'],
  ['Risk Acknowledgement', 'Manual approval, no real money, no real order, kill switch, rollback, and audit requirements.', 'manual approval required'],
  ['Operator Approval Gate', 'The approval gate remains BLOCKED even when simulated approval is requested.', 'sandbox remains disabled'],
  ['Approval Audit Trail', 'Redacted placeholder audit event design.', 'no raw provider payload'],
  ['Safety Validation', 'Validates no sandbox API, secret read, broker connection, order submission, or real money.', 'paper trading only'],
];

export default function V5PreSandboxApprovalPage() {
  return (
    <ProductionShell
      title="V5 Pre-Sandbox Approval"
      eyebrow="Operator Approval Gate"
      description="Design-only approval gate before any future sandbox preparation, with every real path locked."
      activePath="/v5-pre-sandbox-approval"
    >
      <section className="grid">
        <MetricCard title="Gate" value="BLOCKED" description="Operator approval cannot unlock sandbox access in V5.28." />
        <MetricCard title="Sandbox API" value="Disabled" description="No sandbox API or provider portal access." />
        <MetricCard title="Secret Read" value="Disabled" description="No credential read, storage, or API key creation." />
        <MetricCard title="Orders" value="Disabled" description="No real or sandbox order submission." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Approval gate only</h2>
          </div>
          <StatusBadge status="warning">Blocked</StatusBadge>
        </div>
        <p className="muted">
          Pre-sandbox approval gate only. Approval runtime disabled. Operator approval false. Sandbox API disabled. Secret read disabled. Broker connected false. Real money disabled. Paper trading only.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Design</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="No sandbox unlock"
        description="This page intentionally shows approval design only. It does not create accounts, create API keys, read credentials, access provider portals, submit orders, or enable real money."
      />
    </ProductionShell>
  );
}
