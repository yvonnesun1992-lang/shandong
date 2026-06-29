import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Mock Contract Status', 'Offline mock contract validation', 'mock contract runtime disabled'],
  ['Mock Payload Catalog', 'Placeholder provider payload catalog', 'no raw provider payload'],
  ['Schema Validation', 'Payload boundary and required field checks', 'sandbox api disabled'],
  ['Request Mapping Test', 'Internal order to design mapping test', 'order submission disabled'],
  ['Response Normalization Test', 'Mock status normalization test', 'broker connected false'],
  ['Error Mapping Test', 'Mock error to internal error classification', 'no provider endpoint URL'],
  ['Idempotency Test', 'Duplicate protection and retry-safe checks', 'paper trading only'],
  ['Order State Machine Test', 'Blocked submission transitions verified', 'account read disabled'],
  ['Safety Validation', 'No SDK, credentials, network, accounts, or orders', 'real money disabled'],
  ['Final Summary', 'Offline contract verdict and warnings', 'mock contract only'],
];

export default function V5ProviderMockContractPage() {
  return (
    <ProductionShell
      title="V5 Mock Contract"
      eyebrow="Provider Sandbox Connector Mock Contract Test"
      description="Offline mock payload validation for the provider connector design. No sandbox API, no account reads, no orders, and no raw provider payloads."
      activePath="/v5-provider-mock-contract"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Mock contract only" description="Mock contract runtime disabled." />
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
          <StatusBadge status="warning">Mock contract only</StatusBadge>
        </div>
        <p className="muted">
          Mock contract only. Mock contract runtime disabled. Sandbox API disabled. Account read disabled. Order submission disabled. Broker connected false. Real money disabled. Paper trading only.
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
        title="No connector runtime"
        description="This page intentionally shows mock contract state only. It does not connect to sandbox APIs, read accounts, create keys, store raw provider payloads, or submit orders."
      />
    </ProductionShell>
  );
}
