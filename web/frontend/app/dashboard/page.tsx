import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';

const quickLinks = [
  ['Strategy research', '/strategy', 'Generate and review research-ready strategy context.'],
  ['Reports', '/reports', 'Open structured research and archive workflows.'],
  ['Risk', '/risk', 'Review risk controls and stability boundaries.'],
  ['Admin Console', '/admin', 'Check platform readiness in one product view.'],
];

export default function DashboardPage() {
  return (
    <ProductionShell
      title="Dashboard"
      eyebrow="Product Overview"
      description="A clean research dashboard for local demos, system readiness, and safe strategy analysis."
      activePath="/dashboard"
    >
      <div className="summaryStrip">
        <MetricCard title="Backend status" value="Ready" description="Health endpoints are available for local verification." />
        <MetricCard title="V2 readiness" value="Verified" description="Startup, integration, and system doctor checks are documented." />
        <MetricCard title="Environment" value="Demo" description="Local / demo environment with mock billing only." status="Warning" />
      </div>
      <section className="card heroPanel">
        <div>
          <p className="eyebrow">Safety boundaries</p>
          <h2>Research mode only</h2>
          <p className="muted">No broker connection. No auto trading. Mock billing only. Local / demo environment.</p>
        </div>
        <a className="button" href="/admin">
          Open Admin Console
        </a>
      </section>
      <div className="grid">
        {quickLinks.map(([title, href, description]) => (
          <a className="card linkCard" href={href} key={href}>
            <h2>{title}</h2>
            <p className="muted">{description}</p>
          </a>
        ))}
      </div>
      <EmptyState
        title="Loading state: backend can be checked on demand"
        description="If an API is unavailable during a demo, the product shell remains readable and safe."
        actionLabel="View API Docs"
        actionHref="/api-docs"
      />
    </ProductionShell>
  );
}
