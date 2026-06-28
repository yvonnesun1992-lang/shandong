import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';
import {
  fetchV5SandboxConnectorCredentialBoundary,
  fetchV5SandboxConnectorErrorCodes,
  fetchV5SandboxConnectorIdempotency,
  fetchV5SandboxConnectorInterfaceContract,
  fetchV5SandboxConnectorRateLimit,
  fetchV5SandboxConnectorReadiness,
  fetchV5SandboxConnectorRequestSchema,
  fetchV5SandboxConnectorResponseSchema,
  fetchV5SandboxConnectorRetryPolicy,
  fetchV5SandboxConnectorStatus,
} from '../lib/apiClient';

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export default async function V5SandboxConnectorPage() {
  const [statusResult, interfaceResult, requestResult, responseResult, errorsResult, idemResult, rateResult, retryResult, credentialResult, readinessResult] = await Promise.all([
    fetchV5SandboxConnectorStatus(),
    fetchV5SandboxConnectorInterfaceContract(),
    fetchV5SandboxConnectorRequestSchema(),
    fetchV5SandboxConnectorResponseSchema(),
    fetchV5SandboxConnectorErrorCodes(),
    fetchV5SandboxConnectorIdempotency(),
    fetchV5SandboxConnectorRateLimit(),
    fetchV5SandboxConnectorRetryPolicy(),
    fetchV5SandboxConnectorCredentialBoundary(),
    fetchV5SandboxConnectorReadiness(),
  ]);
  const status = asRecord(statusResult.data?.sandbox_connector);
  const interfaceContract = asRecord(interfaceResult.data?.interface_contract);
  const requestSchema = asRecord(requestResult.data?.request_schema);
  const responseSchema = asRecord(responseResult.data?.response_schema);
  const errorCodes = asList(errorsResult.data?.error_codes);
  const idempotency = asRecord(idemResult.data?.idempotency);
  const rateLimit = asRecord(rateResult.data?.rate_limit);
  const retryPolicy = asRecord(retryResult.data?.retry_policy);
  const credentialBoundary = asRecord(credentialResult.data?.credential_boundary);
  const readiness = asRecord(readinessResult.data?.readiness);
  const warnings = readinessResult.warning ?? [];

  return (
    <ProductionShell
      title="V5 Sandbox Connector"
      eyebrow="Sandbox Connector Contract Planning"
      description="Contract-only interface planning for a future broker sandbox connector. Runtime remains disabled."
      activePath="/v5-sandbox-connector"
    >
      {!statusResult.ok ? <ErrorState description={statusResult.errorMessage ?? 'Backend unavailable. Showing safe contract fallback state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Sandbox Connector Contract Status" value="Contract only" description="Connector runtime: disabled" status="Warning" />
        <MetricCard title="Sandbox API" value="Disabled" description="Sandbox API: disabled" status="OK" />
        <MetricCard title="Broker Boundary" value="Disconnected" description="Broker connected: false" status="OK" />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Safety Boundary</h2>
          <StatusBadge status="OK" />
        </div>
        <p>Contract only</p>
        <p>Connector runtime: disabled</p>
        <p>Sandbox API: disabled</p>
        <p>Broker connected: false</p>
        <p>Real orders: disabled</p>
        <p>Real money: disabled</p>
        <p>Paper trading only</p>
      </section>
      <div className="grid">
        <MetricCard title="Interface Contract" value={String(asList(interfaceContract.methods).length || 7)} description="Required future connector methods." />
        <MetricCard title="Request Schema" value={String(asList(requestSchema.submit_order_request).length || 12)} description="Submit, cancel, and status request fields." />
        <MetricCard title="Response Schema" value="Sanitized" description="Provider payload is not exposed." />
        <MetricCard title="Error Codes" value={String(errorCodes.length || 15)} description="Normalized connector error contract." />
        <MetricCard title="Idempotency Policy" value={String(idempotency.duplicate_error_code ?? 'ORDER_DUPLICATE')} description="Stable local key planning." />
        <MetricCard title="Final Verdict" value={String(asRecord(readiness.safety).safe ?? true)} description="Runtime disabled and contract-only." status="Warning" />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Connector Contract</h2>
            <StatusBadge status="Warning" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ status, interfaceContract, requestSchema, responseSchema }, null, 2)}</pre>
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Policies</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ errorCodes, idempotency, rateLimit, retryPolicy, credentialBoundary, readiness }, null, 2)}</pre>
        </section>
      </div>
      {warnings.length ? <EmptyState title="Sandbox connector planning warnings" description={warnings.join(' | ')} /> : null}
    </ProductionShell>
  );
}
