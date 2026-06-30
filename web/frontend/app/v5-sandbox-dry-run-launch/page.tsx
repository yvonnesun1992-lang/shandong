import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Sandbox Dry-Run Launch', 'Launch-plan-only status and provider selection.', 'runtime disabled'],
  ['Dry-Run Scope', 'Read-only-first scope with simulated account read, order preview, approval, kill switch, and rollback.', 'simulate only'],
  ['Feature Flags', 'Dry-run runtime, sandbox API, secret read, account read, order preview, order submission, and real money flags stay locked.', 'flags disabled'],
  ['Responsibility Matrix', 'Strategy, technical, risk, compliance, vault, and emergency roles.', 'no role can enable real paths'],
  ['Preflight Checklist', 'Evidence, approval gate, vault design, feature flags, kill switch, rollback, audit, and compliance review placeholders.', 'not ready'],
  ['Launch Sequence', 'Fourteen-step launch sequence represented as simulation steps only.', 'no real execution'],
  ['Rollback Plan', 'Keeps sandbox API, secret read, account read, and order submission disabled.', 'paper-only fallback'],
  ['Go / No-Go Gate', 'The V5.29 gate remains NO_GO.', 'launch not allowed'],
];

export default function V5SandboxDryRunLaunchPage() {
  return (
    <ProductionShell
      title="V5 Dry-Run Launch"
      eyebrow="Sandbox Dry-Run Launch Plan"
      description="Plan-only launch control for a future sandbox dry-run, with every runtime and real path locked."
      activePath="/v5-sandbox-dry-run-launch"
    >
      <section className="grid">
        <MetricCard title="Gate" value="NO_GO" description="Dry-run launch is not allowed in V5.29." />
        <MetricCard title="Sandbox API" value="Disabled" description="No sandbox API or provider portal access." />
        <MetricCard title="Secret / Account Read" value="Disabled" description="No credential, account, balance, or position read." />
        <MetricCard title="Orders" value="Disabled" description="No real or sandbox order submission." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Launch plan only</h2>
          </div>
          <StatusBadge status="warning">NO_GO</StatusBadge>
        </div>
        <p className="muted">
          Sandbox dry-run launch plan only. Launch runtime disabled. Sandbox API disabled. Secret read disabled. Account read disabled. Broker connected false. Real money disabled. Paper trading only.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Plan</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="No sandbox launch"
        description="This page intentionally shows launch planning only. It does not create accounts, create API keys, read credentials, read accounts, submit orders, or enable real money."
      />
    </ProductionShell>
  );
}
