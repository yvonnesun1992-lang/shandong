import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge, type StatusTone } from '../components/StatusBadge';
import { fetchV5DeploymentDryRun, fetchV5DeploymentReadiness } from '../lib/apiClient';

const fallbackDeployment = {
  version: 'V5.5',
  mode: 'dry_run',
  deployment_mode: 'dry_run',
  runtime_mode: 'paper',
  monitoring_mode: 'local',
  storage_mode: 'local_files',
  dry_run_ready: false,
  deployment_ready: false,
  paper_trading: true,
  real_trading: false,
  broker_connected: false,
  real_money_enabled: false,
  production_deployment: false,
  checks: [],
  warnings: ['Backend unavailable. Showing safe dry run fallback.'],
};

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function tone(value: unknown): StatusTone {
  const text = String(value ?? '').toLowerCase();
  if (text.includes('false') || text.includes('fail') || text.includes('error')) return 'Error';
  if (text.includes('warning') || text.includes('planned')) return 'Warning';
  return 'OK';
}

function listCount(value: unknown) {
  return Array.isArray(value) ? value.length : 0;
}

export default async function V5DeploymentPage() {
  const [dryRunResult, readinessResult] = await Promise.all([fetchV5DeploymentDryRun(), fetchV5DeploymentReadiness()]);
  const deployment = {
    ...fallbackDeployment,
    ...asRecord(asRecord(dryRunResult.data).deployment),
  };
  const readiness = asRecord(asRecord(readinessResult.data).deployment);
  const checks = (deployment.checks as unknown[]) ?? [];
  const warnings = (deployment.warnings as unknown[]) ?? [];

  return (
    <ProductionShell
      title="V5 Deployment"
      eyebrow="Production Deployment Dry Run"
      description="Deployment-shape validation for the V5 paper trading runtime, monitoring API, frontend dashboard, Docker files, startup checks, and health endpoints."
      activePath="/v5-deployment"
    >
      {!dryRunResult.ok ? <ErrorState description={dryRunResult.errorMessage ?? 'Backend unavailable. Showing safe fallback deployment state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Deployment Dry Run Status" value={deployment.dry_run_ready ? 'Ready' : 'Review'} description="Dry run readiness only; not a production launch." status={deployment.dry_run_ready ? 'OK' : 'Warning'} />
        <MetricCard title="Deployment Mode" value={String(deployment.deployment_mode)} description="Deployment mode: dry run" status="Warning" />
        <MetricCard title="Final Verdict" value={deployment.deployment_ready ? 'Deployable' : 'Dry run only'} description="Production deployment remains disabled." status={deployment.deployment_ready ? 'OK' : 'Warning'} />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Paper Trading Safety Boundary</h2>
          <StatusBadge status="Warning" />
        </div>
        <p>Paper trading only</p>
        <p>Real trading: disabled</p>
        <p>Broker: not connected</p>
        <p>Real money: disabled</p>
        <p>Production deployment: not enabled</p>
        <p>Deployment mode: dry run</p>
      </section>
      <div className="grid">
        <MetricCard title="Runtime Readiness" value={String(deployment.runtime_mode)} description="V5.0-V5.2 runtime modules are checked." status={tone(deployment.runtime_mode)} />
        <MetricCard title="Monitoring API Readiness" value={String(deployment.monitoring_mode)} description="V5.4 monitoring endpoints are checked." status={tone(deployment.monitoring_mode)} />
        <MetricCard title="Docker / Config Readiness" value={String(deployment.storage_mode)} description="Docker and local config files are checked." status={tone(deployment.storage_mode)} />
        <MetricCard title="Checks" value={String(listCount(checks))} description="Deployment dry run check count." />
        <MetricCard title="Warnings" value={String(listCount(warnings))} description="Warnings do not imply production readiness." status={listCount(warnings) > 0 ? 'Warning' : 'OK'} />
        <MetricCard title="Readiness API" value={readiness.dry_run_ready ? 'Available' : 'Fallback'} description="Readiness endpoint response status." status={readiness.dry_run_ready ? 'OK' : 'Warning'} />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Missing Production Requirements</h2>
          <StatusBadge status="Warning" />
        </div>
        <p>Formal launch target remains unselected.</p>
        <p>Cloud runtime remains planned only.</p>
        <p>Managed storage remains planned only.</p>
        <p>Identity provider remains planned only.</p>
        <p>External log shipping remains disabled.</p>
      </section>
      <section className="card">
        <div className="cardHeader">
          <h2>Readiness Checks</h2>
          <StatusBadge status={checks.length ? 'OK' : 'Warning'} />
        </div>
        {checks.length ? <pre className="codeBlock">{JSON.stringify(checks.slice(0, 24), null, 2)}</pre> : <EmptyState title="No checks loaded" description="The page can render safely before the backend is available." />}
      </section>
    </ProductionShell>
  );
}
