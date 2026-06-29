import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Connector Design Status', 'Design-only connector blueprint', 'connector runtime disabled'],
  ['Field Mapping', 'Internal fields mapped to provider placeholders', 'requires future docs'],
  ['Order Request Mapping', 'Internal schema to provider placeholder schema', 'order submission disabled'],
  ['Order Response Mapping', 'Provider response to normalized placeholder response', 'raw response redacted only'],
  ['Account / Position Mapping', 'Account and position placeholders only', 'account read disabled'],
  ['Error Mapping', 'Provider placeholder errors to internal errors', 'manual review remains required'],
  ['Rate Limit Policy', 'Budget, burst, cooldown, queue, and circuit breaker placeholders', 'sandbox api disabled'],
  ['Idempotency Policy', 'Duplicate protection and retry-safe design', 'paper trading only'],
  ['Order State Machine', 'Submission remains blocked before runtime', 'broker connected false'],
  ['Safety Boundary', 'No SDK, credentials, account reads, or orders', 'real money disabled'],
];

export default function V5ProviderConnectorDesignPage() {
  return (
    <ProductionShell
      title="V5 Connector Design"
      eyebrow="Provider-Specific Sandbox Connector Design"
      description="Design-only mapping layer for the selected provider. No runtime connector, no sandbox API, no account reads, and no order submission."
      activePath="/v5-provider-connector-design"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Design only" description="Connector runtime disabled." />
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
          <StatusBadge status="warning">Design only</StatusBadge>
        </div>
        <p className="muted">
          Design only. Connector runtime disabled. Sandbox API disabled. Account read disabled. Order submission disabled. Broker connected false. Real money disabled. Paper trading only.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Placeholder</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="No connector execution"
        description="This page intentionally shows design state only. It does not connect to sandbox APIs, read accounts, create keys, or submit orders."
      />
    </ProductionShell>
  );
}
