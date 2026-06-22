import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { AuthStatus } from '../components/AuthStatus';
import { LoadingState } from '../components/LoadingState';
import { MetricCard } from '../components/MetricCard';
import { PermissionNotice } from '../components/PermissionNotice';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge, type StatusTone } from '../components/StatusBadge';
import { fetchAdminConsole } from '../lib/apiClient';

type ConsoleModule = {
  key: string;
  title: string;
  status: StatusTone;
  description: string;
  metric: string;
  detail: string;
};

const fallbackConsole: Record<string, ConsoleModule> = {
  system: {
    key: 'system',
    title: 'System Overview',
    status: 'OK',
    description: 'Core runtime, startup checks, and release documents are present.',
    metric: '21 checks',
    detail: 'Local startup verification is ready.',
  },
  api: {
    key: 'api',
    title: 'API Health',
    status: 'OK',
    description: 'FastAPI v2 endpoints respond with standard product responses.',
    metric: '7 endpoints',
    detail: 'Health, readiness, liveness, and admin routes are covered.',
  },
  database: {
    key: 'database',
    title: 'Database',
    status: 'OK',
    description: 'SQLite local storage and repeatable migrations are available.',
    metric: 'SQLite',
    detail: 'PostgreSQL-ready structure remains documented.',
  },
  security: {
    key: 'security',
    title: 'Auth & Security',
    status: 'Warning',
    description: 'Local mode is convenient for demos; production mode requires hardened access.',
    metric: 'Local mode',
    detail: 'Mock login remains a documented foundation.',
  },
  identity: {
    key: 'identity',
    title: 'Identity Provider',
    status: 'Warning',
    description: 'Demo identity is active. Production identity: planned. External provider: not connected.',
    metric: 'Demo identity',
    detail: 'OAuth: not connected. Password storage: none.',
  },
  observability: {
    key: 'observability',
    title: 'Observability',
    status: 'OK',
    description: 'Local observability summarizes API metrics and health timeline without exporting raw logs.',
    metric: 'Local observability',
    detail: 'External provider: not connected. API metrics: available. Health timeline: available. Log export: not connected.',
  },
  workspace: {
    key: 'workspace',
    title: 'Workspace',
    status: 'OK',
    description: 'Default workspace and tenant isolation foundations are visible.',
    metric: 'Isolated',
    detail: 'Workspace access checks are covered by tests.',
  },
  billing: {
    key: 'billing',
    title: 'Plan / Quota',
    status: 'OK',
    description: 'Mock plan, usage, and quota layers are available for product demos.',
    metric: 'Mock billing',
    detail: 'No real payment execution.',
  },
  deployment: {
    key: 'deployment',
    title: 'Deployment',
    status: 'OK',
    description: 'Startup, readiness, liveness, and runbook documents are in place.',
    metric: 'Ops ready',
    detail: 'Deployment examples remain local-safe.',
  },
  deployment_dry_run: {
    key: 'deployment_dry_run',
    title: 'Deployment Dry Run',
    status: 'Warning',
    description: 'Deployment mode: local. Target: local / docker / external planned.',
    metric: 'Dry run ready',
    detail: 'External deployment: not connected. Secrets: not configured. Dry run check: available. Production launch: not enabled.',
  },
  release_candidate: {
    key: 'release_candidate',
    title: 'Release Candidate Freeze',
    status: 'OK',
    description: 'Version: V3.6. Demo ready: yes. External services: not connected.',
    metric: 'Product demo freeze',
    detail: 'Broker: not connected. Real payment: not enabled. Production identity: not enabled. Deployment: dry run only.',
  },
};

function statusFrom(value: unknown): StatusTone {
  const text = String(value ?? 'ok').toLowerCase();
  if (text.includes('error')) return 'Error';
  if (text.includes('warning')) return 'Warning';
  return 'OK';
}

function moduleFromApi(key: string, fallback: ConsoleModule, payload: Record<string, unknown>): ConsoleModule {
  const section = payload[key] as Record<string, unknown> | undefined;
  if (!section) return fallback;
  const warningCount = Array.isArray(section.warnings) ? section.warnings.length : 0;
  return {
    ...fallback,
    status: statusFrom(section.status),
    metric: String(section.status ?? fallback.metric),
    detail: `${warningCount} warning${warningCount === 1 ? '' : 's'}`,
  };
}

export default async function AdminConsolePage() {
  const result = await fetchAdminConsole();
  const adminPayload = ((result.data?.admin_console as Record<string, unknown> | undefined) ?? {}) as Record<string, unknown>;
  const modules = Object.entries(fallbackConsole).map(([key, fallback]) => moduleFromApi(key, fallback, adminPayload));
  const warningCount = result.warning.length;

  return (
    <ProductionShell
      title="Admin Console"
      eyebrow="Product Control Center"
      description="A single, demo-friendly view of API, database, security, workspace, quota, deployment, and release readiness."
      activePath="/admin"
    >
      <AuthStatus />
      {!result.ok ? <ErrorState description={result.errorMessage ?? 'Backend API is unavailable. Showing safe fallback data.'} /> : null}
      {!result.ok ? <PermissionNotice mode={result.errorMessage?.includes('Permission') ? 'denied' : result.errorMessage?.includes('Session') ? 'expired' : 'login'} /> : null}
      {!result.data && !result.errorMessage ? <LoadingState /> : null}
      <div className="summaryStrip">
        <MetricCard title="Control Center" value={result.ok ? 'Connected' : 'Fallback'} description="Admin Console reads backend data when available." />
        <MetricCard title="Safety Boundary" value="Research" description="No broker connection, no auto trading, mock billing only." status="Warning" />
        <MetricCard title="Warnings" value={String(warningCount)} description="API warnings are counted without exposing private values." />
      </div>
      <div className="grid">
        {modules.map((item) => (
          <section className="card moduleCard" key={item.key}>
            <div className="cardHeader">
              <h2>{item.title}</h2>
              <StatusBadge status={item.status} />
            </div>
            <p className="moduleMetric">{item.metric}</p>
            <p className="muted">{item.description}</p>
            <div className="divider" />
            <p className="meta">{item.detail}</p>
            <p className="meta">Last checked: backend request with safe fallback</p>
          </section>
        ))}
      </div>
      <EmptyState
        title="Empty state: no live operations connected"
        description="Admin Console is safe for demos. Fallback mode remains visible when demo auth is missing or the backend is unavailable."
        actionLabel="Open Local Demo Guide"
        actionHref="/api-docs"
      />
    </ProductionShell>
  );
}
