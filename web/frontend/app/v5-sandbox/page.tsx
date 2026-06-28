import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge, type StatusTone } from '../components/StatusBadge';
import { fetchV5SandboxCredentialPolicy, fetchV5SandboxOrderLifecycle, fetchV5SandboxProviderPlan, fetchV5SandboxRollbackPlan, fetchV5SandboxSafetyChecklist, fetchV5SandboxStatus } from '../lib/apiClient';

const fallback = {
  sandbox_connection_enabled: false,
  sandbox_orders_enabled: false,
  broker_connected: false,
  real_orders_enabled: false,
  real_money_enabled: false,
  paper_trading: true,
  planning_only: true,
};

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function tone(value: unknown): StatusTone {
  const text = String(value ?? '').toLowerCase();
  if (text.includes('fail') || text.includes('error')) return 'Error';
  if (text.includes('warning') || text.includes('not_ready') || text.includes('planning')) return 'Warning';
  return 'OK';
}

export default async function V5SandboxPage() {
  const [statusResult, providerResult, credentialResult, lifecycleResult, checklistResult, rollbackResult] = await Promise.all([
    fetchV5SandboxStatus(),
    fetchV5SandboxProviderPlan(),
    fetchV5SandboxCredentialPolicy(),
    fetchV5SandboxOrderLifecycle(),
    fetchV5SandboxSafetyChecklist(),
    fetchV5SandboxRollbackPlan(),
  ]);
  const status = { ...fallback, ...asRecord(asRecord(statusResult.data).sandbox) };
  const providerPlan = asRecord(providerResult.data?.provider_plan);
  const credentialPolicy = asRecord(credentialResult.data?.credential_policy);
  const lifecycle = asRecord(lifecycleResult.data?.order_lifecycle);
  const checklist = asRecord(checklistResult.data?.safety_checklist);
  const rollback = asRecord(rollbackResult.data?.rollback_plan);
  const missing = asList(credentialPolicy.missing_requirements);
  const blocking = asList(checklist.blocking_items);
  const warnings = [...(statusResult.warning ?? []), ...(providerResult.warning ?? []), ...(lifecycleResult.warning ?? []), ...(checklistResult.warning ?? []), ...(rollbackResult.warning ?? [])];

  return (
    <ProductionShell
      title="V5 Sandbox"
      eyebrow="Broker Sandbox Readiness Planning"
      description="Planning-only sandbox readiness layer. No sandbox API connection or sandbox order submission is enabled."
      activePath="/v5-sandbox"
    >
      {!statusResult.ok ? <ErrorState description={statusResult.errorMessage ?? 'Backend unavailable. Showing safe sandbox readiness fallback state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Sandbox Readiness Status" value="Planning only" description="Sandbox connection: disabled" status="Warning" />
        <MetricCard title="Sandbox Orders" value="Disabled" description="Sandbox orders: disabled" status="OK" />
        <MetricCard title="Broker Boundary" value="Disconnected" description="Broker connected: false" status="OK" />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Safety Boundary</h2>
          <StatusBadge status="Warning" />
        </div>
        <p>Sandbox connection: disabled</p>
        <p>Sandbox orders: disabled</p>
        <p>Broker connected: false</p>
        <p>Real orders: disabled</p>
        <p>Real money: disabled</p>
        <p>Paper trading only</p>
        <p>Planning only</p>
      </section>
      <div className="grid">
        <MetricCard title="Provider Plan" value={String(providerPlan.provider ?? status.sandbox_provider ?? 'none')} description="Provider readiness only, no SDK loaded." status={tone(providerPlan.readiness)} />
        <MetricCard title="Credential Isolation Policy" value={String(credentialPolicy.future_vault_required ?? true)} description="Future vault required; frontend never receives credentials." status="Warning" />
        <MetricCard title="Sandbox Order Lifecycle" value={String(lifecycle.order_release_policy ?? 'planned_only')} description="Order release remains rejected by default." status="Warning" />
        <MetricCard title="Safety Checklist" value={String(asList(checklist.checks).length || 10)} description="Readiness gates before sandbox work." />
        <MetricCard title="Rollback Plan" value={String(asList(rollback.steps).length || 9)} description="Paper-only rollback planning." />
        <MetricCard title="Missing Requirements" value={String(missing.length + blocking.length)} description="Items blocking sandbox connection/orders." status="Warning" />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Provider Plan</h2>
            <StatusBadge status="Warning" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ status, providerPlan, credentialPolicy }, null, 2)}</pre>
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Sandbox Order Lifecycle</h2>
            <StatusBadge status="Warning" />
          </div>
          {Object.keys(lifecycle).length ? <pre className="codeBlock">{JSON.stringify({ lifecycle, checklist, rollback }, null, 2)}</pre> : <EmptyState title="No lifecycle payload loaded" description="The page renders safely before sandbox planning data is available." />}
        </section>
      </div>
      {warnings.length ? <EmptyState title="Sandbox planning warnings" description={warnings.join(' | ')} /> : null}
    </ProductionShell>
  );
}
