import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';
import {
  fetchV5TransitionCredentialVault,
  fetchV5TransitionEnvironments,
  fetchV5TransitionFeatureFlags,
  fetchV5TransitionKillSwitch,
  fetchV5TransitionReadiness,
  fetchV5TransitionRealOrderBlocker,
  fetchV5TransitionRollback,
  fetchV5TransitionSafety,
  fetchV5TransitionSandboxChecklist,
  fetchV5TransitionStatus,
} from '../lib/apiClient';

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

export default async function V5TransitionPage() {
  const [statusResult, readinessResult, vaultResult, envResult, flagsResult, checklistResult, blockerResult, killResult, rollbackResult, safetyResult] =
    await Promise.all([
      fetchV5TransitionStatus(),
      fetchV5TransitionReadiness(),
      fetchV5TransitionCredentialVault(),
      fetchV5TransitionEnvironments(),
      fetchV5TransitionFeatureFlags(),
      fetchV5TransitionSandboxChecklist(),
      fetchV5TransitionRealOrderBlocker(),
      fetchV5TransitionKillSwitch(),
      fetchV5TransitionRollback(),
      fetchV5TransitionSafety(),
    ]);

  const status = asRecord(statusResult.data?.status);
  const readiness = asRecord(readinessResult.data?.readiness);
  const vault = asRecord(vaultResult.data?.credential_vault);
  const environments = asRecord(envResult.data?.environments);
  const featureFlags = asRecord(flagsResult.data?.feature_flags);
  const checklist = asRecord(checklistResult.data?.sandbox_checklist);
  const blocker = asRecord(blockerResult.data?.real_order_blocker);
  const killSwitch = asRecord(killResult.data?.kill_switch);
  const rollback = asRecord(rollbackResult.data?.rollback);
  const safety = asRecord(safetyResult.data?.safety);
  const warnings = [...(statusResult.warning ?? []), ...(safetyResult.warning ?? [])];

  return (
    <ProductionShell
      title="V5 Transition"
      eyebrow="Sandbox to Real Broker Transition Blueprint"
      description="Final readiness blueprint before any future broker sandbox provider work. blueprint only."
      activePath="/v5-transition"
    >
      {!statusResult.ok ? <ErrorState description={statusResult.errorMessage ?? 'Backend unavailable. Showing safe transition state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Transition Status" value="blueprint only" description="transition disabled" status="OK" />
        <MetricCard title="Sandbox API" value="disabled" description="sandbox api disabled" status="OK" />
        <MetricCard title="Broker" value="disconnected" description="broker connected false" status="OK" />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Safety Boundary</h2>
          <StatusBadge status="OK" />
        </div>
        <p>blueprint only</p>
        <p>transition disabled</p>
        <p>sandbox api disabled</p>
        <p>broker connected false</p>
        <p>real orders disabled</p>
        <p>real money disabled</p>
        <p>paper trading only</p>
      </section>
      <div className="grid">
        <MetricCard title="Readiness Blueprint" value={String(Array.isArray(readiness.sections) ? readiness.sections.length : 9)} description="All real transition readiness remains false." />
        <MetricCard title="Credential Vault Blueprint" value={String(vault.future_vault_required ?? true)} description="Future vault and rotation plan required." />
        <MetricCard title="Environment Separation" value="5" description="local, test, staging, sandbox, production." />
        <MetricCard title="Feature Flags" value="safe" description="Real path flags remain false." />
        <MetricCard title="Sandbox Enablement Checklist" value={String(Array.isArray(checklist.checklist) ? checklist.checklist.length : 12)} description="All future enablement items block current activation." />
        <MetricCard title="Real Order Blocker" value={String(blocker.blocked ?? true)} description="Every real order attempt is blocked." />
        <MetricCard title="Kill Switch Blueprint" value={String(Array.isArray(killSwitch.controls) ? killSwitch.controls.length : 9)} description="Global, connector, and order kill switches planned." />
        <MetricCard title="Rollback Blueprint" value={String(Array.isArray(rollback.steps) ? rollback.steps.length : 9)} description="Paper-only rollback path planned." />
        <MetricCard title="Safety Validation" value={String(safety.safe ?? true)} description="No real connection or order path." status="OK" />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Transition Status</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ status, featureFlags, checklist }, null, 2)}</pre>
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Safety Validation</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ environments, blocker, killSwitch, rollback, safety }, null, 2)}</pre>
        </section>
      </div>
      {warnings.length ? <EmptyState title="Transition blueprint warnings" description={warnings.join(' | ')} /> : null}
    </ProductionShell>
  );
}
