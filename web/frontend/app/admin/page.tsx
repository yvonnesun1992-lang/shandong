import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge, type StatusTone } from '../components/StatusBadge';

type ConsoleModule = {
  title: string;
  status: StatusTone;
  description: string;
  metric: string;
  detail: string;
};

const lastChecked = 'Last checked: local demo snapshot';

const modules: ConsoleModule[] = [
  {
    title: 'System Overview',
    status: 'OK',
    description: 'Core runtime, startup checks, and release documents are present.',
    metric: '21 checks',
    detail: 'Local startup verification is ready.',
  },
  {
    title: 'API Health',
    status: 'OK',
    description: 'FastAPI v2 endpoints respond with standard product responses.',
    metric: '7 endpoints',
    detail: 'Health, readiness, liveness, and admin routes are covered.',
  },
  {
    title: 'Database',
    status: 'OK',
    description: 'SQLite local storage and repeatable migrations are available.',
    metric: 'SQLite',
    detail: 'PostgreSQL-ready structure remains documented.',
  },
  {
    title: 'Auth & Security',
    status: 'Warning',
    description: 'Local mode is convenient for demos; production mode requires hardened access.',
    metric: 'Local mode',
    detail: 'Mock login remains a documented foundation.',
  },
  {
    title: 'Workspace',
    status: 'OK',
    description: 'Default workspace and tenant isolation foundations are visible.',
    metric: 'Isolated',
    detail: 'Workspace access checks are covered by tests.',
  },
  {
    title: 'Plan / Quota',
    status: 'OK',
    description: 'Mock plan, usage, and quota layers are available for product demos.',
    metric: 'Mock billing',
    detail: 'No real payment execution.',
  },
  {
    title: 'Deployment',
    status: 'OK',
    description: 'Startup, readiness, liveness, and runbook documents are in place.',
    metric: 'Ops ready',
    detail: 'Deployment examples remain local-safe.',
  },
  {
    title: 'Release Candidate',
    status: 'OK',
    description: 'V2 release candidate docs and architecture review are ready for demo.',
    metric: 'V2.9',
    detail: 'Architecture review and local demo guide are complete.',
  },
];

export default function AdminConsolePage() {
  return (
    <ProductionShell
      title="Admin Console"
      eyebrow="Product Control Center"
      description="A single, demo-friendly view of API, database, security, workspace, quota, deployment, and release readiness."
      activePath="/admin"
    >
      <div className="summaryStrip">
        <MetricCard title="Control Center" value="Online" description="Fallback product view is ready even when API fetch is unavailable." />
        <MetricCard title="Safety Boundary" value="Research" description="No broker connection, no auto trading, mock billing only." status="Warning" />
        <MetricCard title="Experience" value="Polished" description="Unified cards, badges, spacing, and empty states." />
      </div>
      <div className="grid">
        {modules.map((item) => (
          <section className="card moduleCard" key={item.title}>
            <div className="cardHeader">
              <h2>{item.title}</h2>
              <StatusBadge status={item.status} />
            </div>
            <p className="moduleMetric">{item.metric}</p>
            <p className="muted">{item.description}</p>
            <div className="divider" />
            <p className="meta">{item.detail}</p>
            <p className="meta">{lastChecked}</p>
          </section>
        ))}
      </div>
      <EmptyState
        title="Empty state: no live operations connected"
        description="Admin Console is intentionally safe for demos. It displays platform readiness without exposing private values or live integrations."
        actionLabel="Open Local Demo Guide"
        actionHref="/api-docs"
      />
    </ProductionShell>
  );
}
