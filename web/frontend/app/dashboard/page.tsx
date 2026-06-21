import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { LoadingState } from '../components/LoadingState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import {
  fetchBillingHealth,
  fetchLiveness,
  fetchReadiness,
  fetchSecurityHealth,
  fetchWorkspaceHealth,
} from '../lib/apiClient';

const quickLinks = [
  ['Strategy research', '/strategy', 'Generate and review research-ready strategy context.'],
  ['Reports', '/reports', 'Open structured research and archive workflows.'],
  ['Risk', '/risk', 'Review risk controls and stability boundaries.'],
  ['Admin Console', '/admin', 'Check platform readiness in one product view.'],
];

const fallbackDashboard = {
  backend: 'Fallback',
  liveness: 'Alive',
  readiness: 'Ready',
  security: 'Local mode',
  workspace: 'Workspace ready',
  billing: 'Mock billing only',
};

function statusLabel(value: unknown, fallback: string) {
  if (!value || typeof value !== 'object') return fallback;
  const text = JSON.stringify(value).toLowerCase();
  if (text.includes('warning')) return 'Warning';
  if (text.includes('error')) return 'Needs review';
  if (text.includes('alive')) return 'Alive';
  if (text.includes('ready')) return 'Ready';
  return fallback;
}

export default async function DashboardPage() {
  const [liveness, readiness, security, workspace, billing] = await Promise.all([
    fetchLiveness(),
    fetchReadiness(),
    fetchSecurityHealth(),
    fetchWorkspaceHealth(),
    fetchBillingHealth(),
  ]);
  const apiAvailable = [liveness, readiness, security, workspace, billing].some((item) => item.ok);
  const errorMessage = apiAvailable ? '' : 'Backend API is unavailable. Showing safe fallback dashboard data.';

  return (
    <ProductionShell
      title="Dashboard"
      eyebrow="Product Overview"
      description="A clean research dashboard for local demos, system readiness, and safe strategy analysis."
      activePath="/dashboard"
    >
      {errorMessage ? <ErrorState description={errorMessage} /> : null}
      {!apiAvailable ? <LoadingState label="Preparing fallback dashboard" /> : null}
      <div className="summaryStrip">
        <MetricCard title="Backend status" value={apiAvailable ? 'Connected' : fallbackDashboard.backend} description="Health APIs are checked with safe fallback data." />
        <MetricCard title="Liveness" value={statusLabel(liveness.data, fallbackDashboard.liveness)} description="Service process status for local demos." />
        <MetricCard title="Readiness" value={statusLabel(readiness.data, fallbackDashboard.readiness)} description="Database, auth, workspace, quota, and API readiness." />
      </div>
      <div className="summaryStrip">
        <MetricCard title="Security mode" value={statusLabel(security.data, fallbackDashboard.security)} description="Auth policy is summarized without private values." status="Warning" />
        <MetricCard title="Workspace" value={statusLabel(workspace.data, fallbackDashboard.workspace)} description="Workspace readiness for tenant-style structure." />
        <MetricCard title="Billing" value={statusLabel(billing.data, fallbackDashboard.billing)} description="Mock billing only for product demonstration." status="Warning" />
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
        title="Empty state: no live operations connected"
        description="If an API is unavailable during a demo, the product shell remains readable and safe."
        actionLabel="View API Docs"
        actionHref="/api-docs"
      />
    </ProductionShell>
  );
}
