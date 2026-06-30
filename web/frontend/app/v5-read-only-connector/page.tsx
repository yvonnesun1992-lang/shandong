import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Read-Only Scope', 'Future allowed and disallowed read-only connector actions.', 'not ready'],
  ['Credential Scope', 'Future sandbox read-only permission requirements without frontend access.', 'disabled'],
  ['Account Schema', 'Placeholder-only account snapshot design with redacted provider payload.', 'placeholder'],
  ['Balance Schema', 'Placeholder-only balance snapshot design with values redacted.', 'redacted'],
  ['Position Schema', 'Placeholder-only position snapshot design with quantities and values redacted.', 'redacted'],
  ['Redaction Policy', 'Account refs, balances, positions, provider payload, logs, and frontend values stay redacted.', 'locked'],
  ['Rate Limit Policy', 'Future read budgets, cooldown, backoff, and circuit breaker placeholders.', 'no network'],
  ['Audit Policy', 'Placeholder read audit events with order submitted false.', 'audit only'],
];

export default function V5ReadOnlyConnectorPage() {
  return (
    <ProductionShell
      title="V5 Read-Only Connector"
      eyebrow="Sandbox Dry-Run Read-Only Connector Blueprint"
      description="Blueprint only: no broker connection, sandbox API, credential read, account read, balance read, position read, order preview, order submission, or real money."
      activePath="/v5-read-only-connector"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Blueprint only" description="No runtime connector is enabled." />
        <MetricCard title="Sandbox API" value="Disabled" description="No external network or provider connection." />
        <MetricCard title="Account / Balance / Position" value="Disabled" description="Schemas are placeholders only." />
        <MetricCard title="Orders / Money" value="Disabled" description="No preview execution, submission, or real funds." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Read-only connector blueprint</h2>
          </div>
          <StatusBadge status="warning">Blueprint</StatusBadge>
        </div>
        <p className="muted">
          V5.33 defines future read-only connector schemas, redaction, rate limits, and audit policy. Runtime, sandbox API, credential read, account read, balance read, position read, order preview, order submission, broker connection, and real money remain disabled.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Read-only</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="No connector runtime"
        description="This page intentionally shows read-only connector design only. It does not connect to providers, read credentials, read accounts, read balances, read positions, submit orders, or enable real money."
      />
    </ProductionShell>
  );
}
