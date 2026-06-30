import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Sandbox Preflight Packet', 'Final packet-only material for future sandbox dry-run readiness.', 'runtime disabled'],
  ['Final Preflight Checklist', 'Evidence, review board, disabled paths, provider, blockers, rollback, kill switch, and audit checks.', 'not ready'],
  ['Artifact Manifest', 'Local V5.23-V5.30 reports and validation placeholders.', 'local files only'],
  ['Blocking Item Register', 'NO_GO decision, disabled sandbox paths, vault, account, provider, compliance, audit, kill switch, and rollback blockers.', 'blocked'],
  ['Evidence Digest', 'Replay, fault, soak, evidence, vault, approval, launch, review, gaps, and final decision summary.', 'digest not ready'],
  ['Final NO-GO Record', 'The V5.31 final preflight decision always returns NO_GO.', 'NO_GO'],
  ['Preflight Audit Trail', 'Placeholder audit events with no secret logging, account read, order submission, or sandbox API call.', 'placeholder only'],
  ['Safety Validation', 'Validates no sandbox API, secret read, account read, broker connection, order submission, or real money.', 'paper trading only'],
];

export default function V5SandboxPreflightPacketPage() {
  return (
    <ProductionShell
      title="V5 Preflight Packet"
      eyebrow="Sandbox Dry-Run Final Preflight Packet"
      description="Final preflight packet for a future sandbox dry-run, with every runtime and real path locked."
      activePath="/v5-sandbox-preflight-packet"
    >
      <section className="grid">
        <MetricCard title="Decision" value="NO_GO" description="Sandbox dry-run remains blocked in V5.31." />
        <MetricCard title="Preflight Runtime" value="Disabled" description="No packet approval or runtime path." />
        <MetricCard title="Secret / Account Read" value="Disabled" description="No credential, account, balance, or position read." />
        <MetricCard title="Orders" value="Disabled" description="No real or sandbox order submission." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Preflight packet only</h2>
          </div>
          <StatusBadge status="warning">NO_GO</StatusBadge>
        </div>
        <p className="muted">
          Sandbox dry-run final preflight packet only. Preflight runtime disabled. Packet approval disabled. Sandbox API disabled. Secret read disabled. Account read disabled. Broker connected false. Real money disabled. Paper trading only.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Packet</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="No sandbox launch"
        description="This page intentionally shows preflight packet design only. It does not approve sandbox API, read credentials, read accounts, submit orders, or enable real money."
      />
    </ProductionShell>
  );
}
