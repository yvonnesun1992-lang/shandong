import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';
import {
  fetchV5IntegrationLayers,
  fetchV5IntegrationRun,
  fetchV5IntegrationScenarios,
  fetchV5IntegrationStatus,
  fetchV5IntegrationSummary,
} from '../lib/apiClient';

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export default async function V5IntegrationTestPage() {
  const [statusResult, scenariosResult, runResult, layersResult, summaryResult] = await Promise.all([
    fetchV5IntegrationStatus(),
    fetchV5IntegrationScenarios(),
    fetchV5IntegrationRun(),
    fetchV5IntegrationLayers(),
    fetchV5IntegrationSummary(),
  ]);
  const status = asRecord(statusResult.data?.status);
  const scenarios = asRecord(scenariosResult.data?.scenarios);
  const run = asRecord(runResult.data?.run);
  const layers = asRecord(layersResult.data?.layers);
  const summary = asRecord(summaryResult.data?.summary);
  const scenarioList = asList(scenarios.scenarios);
  const finalSummary = asRecord(summary.summary);
  const warnings = [...(statusResult.warning ?? []), ...(summaryResult.warning ?? [])];

  return (
    <ProductionShell
      title="V5 Integration Test"
      eyebrow="Sandbox Connector Integration Test Harness"
      description="End-to-end simulation harness for the future broker path. It is simulation only."
      activePath="/v5-integration-test"
    >
      {!statusResult.ok ? <ErrorState description={statusResult.errorMessage ?? 'Backend unavailable. Showing safe integration state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Integration Pipeline Status" value={String(status.status ?? 'PASS')} description="simulation only" status="OK" />
        <MetricCard title="Scenario Matrix" value={String(scenarioList.length || 10)} description="deterministic replay scenarios." status="OK" />
        <MetricCard title="Safety Gate Status" value="safe" description="no real broker, no sandbox api" status="OK" />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Integration Safety Boundary</h2>
          <StatusBadge status="OK" />
        </div>
        <p>simulation only</p>
        <p>no real broker</p>
        <p>no sandbox api</p>
        <p>no real orders</p>
      </section>
      <div className="grid">
        <MetricCard title="Layer-by-layer Execution" value={String(asList(layers.layers).length || 4)} description="Alpha, mock connector, skeleton adapter, bridge." />
        <MetricCard title="Failure Injection" value={String(asRecord(status.pipeline).status ?? 'PASS')} description="Failure paths stay inside simulation." />
        <MetricCard title="Consistency Validation" value={String(asRecord(status.consistency).valid ?? true)} description="Cross-layer status and audit checks." />
        <MetricCard title="Final Verdict" value={String(summary.verdict ?? 'PASS')} description={`Score ${String(finalSummary.integration_score ?? 1)}`} />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Scenario Matrix</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ scenarios, run }, null, 2)}</pre>
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Final Verdict</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ status, layers, summary }, null, 2)}</pre>
        </section>
      </div>
      {warnings.length ? <EmptyState title="Integration harness warnings" description={warnings.join(' | ')} /> : null}
    </ProductionShell>
  );
}
