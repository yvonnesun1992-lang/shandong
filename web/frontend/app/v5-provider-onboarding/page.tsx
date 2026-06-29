import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Onboarding Status', 'Runbook only', 'provider portal access disabled'],
  ['Selected Provider', 'Resolved from V5.19 report or fallback config', 'broker connected false'],
  ['Account Opening Runbook', 'Human preparation checklist', 'cannot proceed automatically'],
  ['Sandbox Access Runbook', 'Future sandbox access checklist', 'sandbox api disabled'],
  ['API Key Preparation', 'Future vault and rotation checklist', 'api key creation disabled'],
  ['Market Data Onboarding', 'Entitlement and usage review checklist', 'no market data API access'],
  ['Approval & Risk', 'Manual approval and kill switch preparation', 'real orders disabled'],
  ['Sandbox Dry Run', 'Future dry-run phases only', 'sandbox orders disabled by default'],
  ['Safety Validation', 'Boundary checks remain active', 'real money disabled'],
  ['Blocking Items', 'Production prerequisites remain incomplete', 'paper trading only'],
];

export default function V5ProviderOnboardingPage() {
  return (
    <ProductionShell
      title="V5 Provider Onboarding"
      eyebrow="Selected Provider Sandbox Onboarding Runbook"
      description="Runbook-only preparation for the selected provider. No portal access, no sandbox API, no API key creation, and no broker connection."
      activePath="/v5-provider-onboarding"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Runbook only" description="The system prepares operator checklists but performs no external action." />
        <MetricCard title="Provider Portal" value="Disabled" description="Provider portal access disabled." />
        <MetricCard title="API Key Creation" value="Disabled" description="API key creation disabled and no credentials are stored." />
        <MetricCard title="Sandbox API" value="Disabled" description="Sandbox API disabled; broker connected false." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Paper trading only</h2>
          </div>
          <StatusBadge status="warning">Runbook only</StatusBadge>
        </div>
        <p className="muted">
          Provider portal access disabled. API key creation disabled. Sandbox API disabled. Broker connected false. Real orders disabled. Real money disabled. Paper trading only.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Not ready</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="No provider onboarding execution"
        description="This page intentionally shows preparation state only. It does not create accounts, request keys, read accounts, or send orders."
      />
    </ProductionShell>
  );
}
