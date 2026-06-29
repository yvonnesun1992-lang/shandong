import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Fault Injection Status', 'Offline fault injection boundary and provider selection', 'fault runtime disabled'],
  ['Fault Scenario Catalog', 'Local placeholder fault scenario catalog', 'no endpoint URL field'],
  ['Fault Injector', 'Converts fault scenarios into local placeholder events', 'no provider calls'],
  ['Fault Replay Runner', 'Runs connector timeout, duplicate order, stale response, and other offline faults', 'order submission disabled'],
  ['Detection Validation', 'Timeout, duplicate, stale, order, fill, rate limit, audit, state, and idempotency checks', 'sandbox API disabled'],
  ['Recovery Validation', 'Recovery, rollback, kill switch, audit, and safe final state checks', 'no external retry call'],
  ['Kill Switch Simulation', 'Simulated kill switch only; no real system effect', 'broker connected false'],
  ['Fault Audit Trail', 'Placeholder audit events with redacted provider payload markers', 'raw payload stored false'],
  ['Safety Validation', 'SDK, credential, network, account, order, and endpoint boundaries', 'real money disabled'],
  ['Final Summary', 'Offline fault injection verdict and warnings', 'paper trading only'],
];

export default function V5ProviderFaultInjectionPage() {
  return (
    <ProductionShell
      title="V5 Fault Injection"
      eyebrow="Provider Sandbox Connector Fault Injection Suite"
      description="Offline fault injection validation for mock connector timeout, rejection, duplicate order, stale response, out-of-order event, recovery, audit, and safety paths."
      activePath="/v5-provider-fault-injection"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Fault injection only" description="Fault injection runtime disabled." />
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
          <StatusBadge status="warning">Offline</StatusBadge>
        </div>
        <p className="muted">
          Fault injection only. Fault injection runtime disabled. Sandbox API disabled. Account read disabled. Order submission disabled. Broker connected false. Real money disabled. Paper trading only.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Offline</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="No provider runtime"
        description="This page intentionally shows offline fault injection state only. It does not connect to sandbox APIs, read accounts, create keys, store raw provider payloads, or submit orders."
      />
    </ProductionShell>
  );
}
