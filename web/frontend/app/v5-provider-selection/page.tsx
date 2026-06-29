import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';
import {
  fetchV5ProviderSelectionAccountChecklist,
  fetchV5ProviderSelectionApiPermissions,
  fetchV5ProviderSelectionCapabilityMatrix,
  fetchV5ProviderSelectionCompliance,
  fetchV5ProviderSelectionMarketData,
  fetchV5ProviderSelectionRanking,
  fetchV5ProviderSelectionRiskMatrix,
  fetchV5ProviderSelectionSafety,
  fetchV5ProviderSelectionStatus,
  fetchV5ProviderSelectionUniverse,
} from '../lib/apiClient';

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export default async function V5ProviderSelectionPage() {
  const [statusResult, universeResult, capabilityResult, riskResult, accountResult, apiResult, marketResult, complianceResult, rankingResult, safetyResult] =
    await Promise.all([
      fetchV5ProviderSelectionStatus(),
      fetchV5ProviderSelectionUniverse(),
      fetchV5ProviderSelectionCapabilityMatrix(),
      fetchV5ProviderSelectionRiskMatrix(),
      fetchV5ProviderSelectionAccountChecklist(),
      fetchV5ProviderSelectionApiPermissions(),
      fetchV5ProviderSelectionMarketData(),
      fetchV5ProviderSelectionCompliance(),
      fetchV5ProviderSelectionRanking(),
      fetchV5ProviderSelectionSafety(),
    ]);

  const status = asRecord(statusResult.data?.status);
  const universe = asRecord(universeResult.data?.universe);
  const capability = asRecord(capabilityResult.data?.capability_matrix);
  const risk = asRecord(riskResult.data?.risk_matrix);
  const account = asRecord(accountResult.data?.account_checklist);
  const apiPermissions = asRecord(apiResult.data?.api_permissions);
  const marketData = asRecord(marketResult.data?.market_data);
  const compliance = asRecord(complianceResult.data?.compliance);
  const ranking = asRecord(rankingResult.data?.ranking);
  const safety = asRecord(safetyResult.data?.safety);
  const warnings = [...(statusResult.warning ?? []), ...(safetyResult.warning ?? [])];

  return (
    <ProductionShell
      title="V5 Provider Selection"
      eyebrow="Broker Sandbox Provider Selection & Account Preparation"
      description="Selection-only preparation for future broker sandbox review. No provider connection is enabled."
      activePath="/v5-provider-selection"
    >
      {!statusResult.ok ? <ErrorState description={statusResult.errorMessage ?? 'Backend unavailable. Showing safe provider selection state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Provider Selection Status" value="selection only" description="provider connection disabled" status="OK" />
        <MetricCard title="Sandbox API" value="disabled" description="sandbox api disabled" status="OK" />
        <MetricCard title="Broker" value="disconnected" description="broker connected false" status="OK" />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Safety Boundary</h2>
          <StatusBadge status="OK" />
        </div>
        <p>selection only</p>
        <p>provider connection disabled</p>
        <p>sandbox api disabled</p>
        <p>broker connected false</p>
        <p>real orders disabled</p>
        <p>real money disabled</p>
        <p>paper trading only</p>
      </section>
      <div className="grid">
        <MetricCard title="Provider Universe" value={String(asList(universe.providers).length || 5)} description="Alpaca, IBKR, Futu, Tiger, Schwab." />
        <MetricCard title="Capability Matrix" value={String(asList(capability.matrix).length || 5)} description="Static readiness scoring." />
        <MetricCard title="Risk Matrix" value={String(asList(risk.matrix).length || 5)} description="Static risk review." />
        <MetricCard title="Account Preparation Checklist" value={String(asList(account.checklist).length || 11)} description="Current account ready: false." />
        <MetricCard title="API Permission Checklist" value={String(asList(apiPermissions.permissions).length || 12)} description="API ready: false." />
        <MetricCard title="Market Data Checklist" value={String(asList(marketData.requirements).length || 11)} description="Market data ready: false." />
        <MetricCard title="Compliance Checklist" value={String(asList(compliance.requirements).length || 11)} description="Compliance ready: false." />
        <MetricCard title="Provider Ranking" value={String(asList(ranking.rankings).length || 5)} description="Static ranking only." />
        <MetricCard title="Recommended Provider" value={String(ranking.recommended_provider ?? 'alpaca')} description="Based on static capability/risk score." />
        <MetricCard title="Safety Validation" value={String(safety.safe ?? true)} description="No provider connection or credential path." status="OK" />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Provider Ranking</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ status, universe, ranking }, null, 2)}</pre>
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Safety Validation</h2>
            <StatusBadge status="OK" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ account, apiPermissions, marketData, compliance, safety }, null, 2)}</pre>
        </section>
      </div>
      {warnings.length ? <EmptyState title="Provider selection warnings" description={warnings.join(' | ')} /> : null}
    </ProductionShell>
  );
}
