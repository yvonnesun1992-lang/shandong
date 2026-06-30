import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Payload Catalog', 'Local placeholder account, balance, position, and error snapshots.', 'local only'],
  ['Schema Check', 'Validates placeholder shape without external provider reads.', 'checked'],
  ['Redaction Check', 'Balance and position values remain redacted placeholders.', 'redacted'],
  ['Replay Runner', 'Replays local mock payloads without network calls.', 'mock replay only'],
  ['Audit Replay', 'Records placeholder replay events with all order paths disabled.', 'audit only'],
  ['Safety Gate', 'Blocks runtime, sandbox API, account, balance, position, order, and money paths.', 'locked'],
];

export default function V5ReadOnlyMockReplayPage() {
  return (
    <ProductionShell
      title="V5 Read-Only Mock Replay"
      eyebrow="Sandbox Read-Only Connector Mock Replay"
      description="Mock replay only: local redacted payloads, no provider connection, no account lookup, no balance lookup, no position lookup, no order preview, and no order submission."
      activePath="/v5-read-only-mock-replay"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Mock replay only" description="Local placeholder replay without runtime connector." />
        <MetricCard title="Provider Network" value="Disabled" description="No sandbox API or endpoint access." />
        <MetricCard title="Values" value="Redacted" description="Balance and position values stay placeholders." />
        <MetricCard title="Orders / Money" value="Disabled" description="No preview, submission, broker, or money path." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Read-only mock replay</h2>
          </div>
          <StatusBadge status="warning">Mock</StatusBadge>
        </div>
        <p className="muted">
          V5.34 replays only local placeholder payloads. Runtime connector, sandbox API, credential access, account reads, balance reads, position reads, order preview, order submission, broker connection, and real money remain disabled.
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
        title="No live connector"
        description="This page intentionally shows local mock replay only. It does not connect to providers, read accounts, read balances, read positions, preview orders, submit orders, or enable real funds."
      />
    </ProductionShell>
  );
}
