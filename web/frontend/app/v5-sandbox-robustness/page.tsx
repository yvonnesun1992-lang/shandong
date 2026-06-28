import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';
import {
  fetchV5SandboxRobustnessFaultCombinations,
  fetchV5SandboxRobustnessLongRun,
  fetchV5SandboxRobustnessMultiSymbol,
  fetchV5SandboxRobustnessScenarioMatrix,
  fetchV5SandboxRobustnessStatus,
  fetchV5SandboxRobustnessSummary,
} from '../lib/apiClient';

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export default async function V5SandboxRobustnessPage() {
  const [statusResult, matrixResult, multiResult, faultsResult, longRunResult, summaryResult] = await Promise.all([
    fetchV5SandboxRobustnessStatus(),
    fetchV5SandboxRobustnessScenarioMatrix(),
    fetchV5SandboxRobustnessMultiSymbol(),
    fetchV5SandboxRobustnessFaultCombinations(),
    fetchV5SandboxRobustnessLongRun(),
    fetchV5SandboxRobustnessSummary(),
  ]);
  const status = asRecord(statusResult.data?.sandbox_robustness);
  const matrix = asRecord(matrixResult.data?.scenario_matrix);
  const multi = asRecord(multiResult.data?.multi_symbol);
  const faults = asRecord(faultsResult.data?.fault_combinations);
  const longRun = asRecord(longRunResult.data?.long_run);
  const summary = asRecord(summaryResult.data?.sandbox_robustness);
  const scenarioCount = asList(matrix.scenarios).length || 16;
  const warningCount = Number(longRun.warning_count ?? 0);
  const warnings = [...(statusResult.warning ?? []), ...(longRunResult.warning ?? []), ...(summaryResult.warning ?? [])];

  return (
    <ProductionShell
      title="V5 Sandbox Robustness"
      eyebrow="Sandbox Simulation Robustness Suite"
      description="Local-only robustness validation for sandbox simulation scenarios, faults, consistency, and long-run stability."
      activePath="/v5-sandbox-robustness"
    >
      {!statusResult.ok ? <ErrorState description={statusResult.errorMessage ?? 'Backend unavailable. Showing safe robustness fallback state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Sandbox Robustness Status" value="Local robustness simulation only" description="Sandbox API: disabled" status="OK" />
        <MetricCard title="Broker Boundary" value="Disconnected" description="Broker connected: false" status="OK" />
        <MetricCard title="Order Boundary" value="Simulated" description="Real orders: disabled" status="OK" />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Safety Boundary</h2>
          <StatusBadge status="OK" />
        </div>
        <p>Local robustness simulation only</p>
        <p>Sandbox API: disabled</p>
        <p>Broker connected: false</p>
        <p>Real orders: disabled</p>
        <p>Real money: disabled</p>
        <p>Paper trading only</p>
      </section>
      <div className="grid">
        <MetricCard title="Scenario Matrix" value={String(scenarioCount)} description="Base and combined robustness scenarios." />
        <MetricCard title="Multi-symbol Simulation" value={String(asList(multi.symbols).length || 5)} description="AAPL, MSFT, NVDA, SPY, QQQ." />
        <MetricCard title="Fault Combinations" value={String(faults.combination_count ?? 7)} description="Local-only fault combinations." status="Warning" />
        <MetricCard title="Long-run Robustness" value={String(longRun.final_verdict ?? 'WARNING')} description={`${warningCount} warning scenarios.`} status={warningCount ? 'Warning' : 'OK'} />
        <MetricCard title="Consistency Validation" value={String(asRecord(summary.consistency_validation).valid ?? true)} description="Account, order, fill, audit, and safety checks." />
        <MetricCard title="Final Verdict" value={String(summary.verdict ?? 'WARNING')} description="Sandbox robustness report state." status={String(summary.verdict ?? '').includes('FAIL') ? 'Error' : 'Warning'} />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Scenario Matrix</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ status, matrix, multi }, null, 2)}</pre>
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Faults And Long-run</h2>
            <StatusBadge status="Warning" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ faults, longRun, summary }, null, 2)}</pre>
        </section>
      </div>
      {warnings.length ? <EmptyState title="Sandbox robustness warnings" description={warnings.join(' | ')} /> : null}
    </ProductionShell>
  );
}
