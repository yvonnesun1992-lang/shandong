import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Credential Vault Status', 'Vault design-only boundary and provider selection', 'vault runtime disabled'],
  ['Vault Interface Contract', 'Reference, validation, rotation, revocation, and audit access placeholders', 'placeholder only'],
  ['Scope Policy', 'Sandbox/real and read-only/trading separation plan', 'frontend blocked'],
  ['Access Policy', 'Operator, runtime service, audit service, emergency revoke, and frontend roles', 'all access disabled'],
  ['Rotation / Revocation', 'Scheduled rotation, emergency revoke, suspected leak, provider portal, vault update, CI, audit, and operator confirmation placeholders', 'no provider portal'],
  ['Vault Audit Design', 'Redacted access audit event structure', 'raw secret logged false'],
  ['Safety Validation', 'Runtime, read/write, sandbox, broker, order, money, and credential boundaries', 'real money disabled'],
  ['Final Summary', 'Vault design verdict and warnings', 'paper trading only'],
];

export default function V5CredentialVaultDesignPage() {
  return (
    <ProductionShell
      title="V5 Credential Vault"
      eyebrow="Credential Vault Interface Design"
      description="Design-only vault interface for future sandbox credential handling, with all runtime access disabled."
      activePath="/v5-credential-vault-design"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Vault design only" description="Vault runtime disabled." />
        <MetricCard title="Read / Write" value="Disabled" description="Credential read and write disabled." />
        <MetricCard title="Sandbox API" value="Disabled" description="Sandbox API disabled and no network calls are made." />
        <MetricCard title="Order Submission" value="Disabled" description="Order submission disabled and broker connected false." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Design only</h2>
          </div>
          <StatusBadge status="warning">Blocked</StatusBadge>
        </div>
        <p className="muted">
          Vault design only. Vault runtime disabled. Credential read disabled. Credential write disabled. Sandbox API disabled. Broker connected false. Real money disabled. Paper trading only.
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
        title="No vault runtime"
        description="This page intentionally shows vault interface design only. It does not connect to a vault, read credentials, create provider keys, store raw provider payloads, or submit orders."
      />
    </ProductionShell>
  );
}
