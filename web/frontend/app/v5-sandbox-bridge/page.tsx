import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';
import {
  fetchV5SandboxBridgeIdempotency,
  fetchV5SandboxBridgeNormalize,
  fetchV5SandboxBridgeRetry,
  fetchV5SandboxBridgeRouting,
  fetchV5SandboxBridgeSafety,
  fetchV5SandboxBridgeSession,
  fetchV5SandboxBridgeStatus,
  fetchV5SandboxBridgeTransform,
} from '../lib/apiClient';

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

export default async function V5SandboxBridgePage() {
  const [statusResult, sessionResult, routingResult, transformResult, normalizeResult, retryResult, idempotencyResult, safetyResult] = await Promise.all([
    fetchV5SandboxBridgeStatus(),
    fetchV5SandboxBridgeSession(),
    fetchV5SandboxBridgeRouting(),
    fetchV5SandboxBridgeTransform(),
    fetchV5SandboxBridgeNormalize(),
    fetchV5SandboxBridgeRetry(),
    fetchV5SandboxBridgeIdempotency(),
    fetchV5SandboxBridgeSafety(),
  ]);
  const status = asRecord(statusResult.data?.status);
  const session = asRecord(sessionResult.data?.session);
  const routing = asRecord(routingResult.data?.routing);
  const transform = asRecord(transformResult.data?.transform);
  const normalize = asRecord(normalizeResult.data?.normalize);
  const retry = asRecord(retryResult.data?.retry);
  const idempotency = asRecord(idempotencyResult.data?.idempotency);
  const safety = asRecord(safetyResult.data?.safety);
  const summary = asRecord(safetyResult.data?.summary);
  const warnings = [...(statusResult.warning ?? []), ...(safetyResult.warning ?? [])];

  return (
    <ProductionShell
      title="V5 Sandbox Bridge"
      eyebrow="Sandbox Connector Bridge"
      description="Bridge-only abstraction layer for a future sandbox connector. No external runtime is enabled."
      activePath="/v5-sandbox-bridge"
    >
      {!statusResult.ok ? <ErrorState description={statusResult.errorMessage ?? 'Backend unavailable. Showing safe bridge state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Bridge Status" value="bridge only" description="no real connection" status="OK" />
        <MetricCard title="Safety Gate" value={String(safety.safe ?? true)} description="no broker, no sandbox API" status="OK" />
        <MetricCard title="Execution Boundary" value="paper trading only" description="no real orders" status="OK" />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Bridge Safety Boundary</h2>
          <StatusBadge status="OK" />
        </div>
        <p>no real connection</p>
        <p>no broker</p>
        <p>no sandbox API</p>
        <p>paper trading only</p>
      </section>
      <div className="grid">
        <MetricCard title="Session Lifecycle" value={String(session.state ?? 'CONNECTED_SIMULATED')} description="Simulated bridge lifecycle only." />
        <MetricCard title="Routing Layer" value={String(routing.backend ?? 'bridge')} description="Mock, skeleton, or bridge simulated route." />
        <MetricCard title="Request Transform" value={String(transform.request_type ?? 'submit_order')} description="Local schema transform." />
        <MetricCard title="Response Normalize" value={String(normalize.response_type ?? 'order')} description="Sanitized V5 response format." />
        <MetricCard title="Error Translation" value={String(asRecord(retryResult.data?.error_translation).error_code ?? 'TIMEOUT')} description="Standardized bridge errors." />
        <MetricCard title="Retry Policy" value={String(retry.should_retry ?? true)} description="Delay plan only; no real sleep." />
        <MetricCard title="Idempotency" value={String(idempotency.duplicate ?? true)} description="Local duplicate detection." />
        <MetricCard title="Final Verdict" value={String(summary.verdict ?? 'PASS')} description="Bridge abstraction is safe for review." />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Bridge Status</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ status, session, routing, transform }, null, 2)}</pre>
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Safety Gate</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ normalize, retry, idempotency, safety, summary }, null, 2)}</pre>
        </section>
      </div>
      {warnings.length ? <EmptyState title="Sandbox bridge warnings" description={warnings.join(' | ')} /> : null}
    </ProductionShell>
  );
}
