import { EmptyState } from '../components/EmptyState';
import { ErrorState } from '../components/ErrorState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge, type StatusTone } from '../components/StatusBadge';
import { fetchV5ApprovalAuditSummary, fetchV5ApprovalPolicy, fetchV5ApprovalReadiness, fetchV5ApprovalStatus } from '../lib/apiClient';

const fallback = {
  manual_approval_required: true,
  auto_approval_enabled: false,
  real_order_after_approval: false,
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
  if (text.includes('warning') || text.includes('planning')) return 'Warning';
  return 'OK';
}

export default async function V5ApprovalPage() {
  const [statusResult, readinessResult, policyResult, auditResult] = await Promise.all([
    fetchV5ApprovalStatus(),
    fetchV5ApprovalReadiness(),
    fetchV5ApprovalPolicy(),
    fetchV5ApprovalAuditSummary(),
  ]);
  const status = { ...fallback, ...asRecord(asRecord(statusResult.data).approval) };
  const readiness = asRecord(readinessResult.data?.readiness);
  const policy = asRecord(policyResult.data?.policy);
  const audit = asRecord(auditResult.data?.audit_summary);
  const missing = asList(readiness.missing_production_requirements);
  const warnings = [...(statusResult.warning ?? []), ...(readinessResult.warning ?? [])];

  return (
    <ProductionShell
      title="V5 Approval"
      eyebrow="Manual Approval Gate Planning"
      description="Planning-only manual review gate for future order release. Simulated approval never enables real orders."
      activePath="/v5-approval"
    >
      {!statusResult.ok ? <ErrorState description={statusResult.errorMessage ?? 'Backend unavailable. Showing safe manual approval fallback state.'} /> : null}
      <div className="summaryStrip">
        <MetricCard title="Manual Approval Gate Status" value="Planning only" description="Manual approval required: true" status="Warning" />
        <MetricCard title="Auto Approval" value="Disabled" description="Auto approval: disabled" status="OK" />
        <MetricCard title="Order Release" value="Disabled" description="Real orders: disabled" status="OK" />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Safety Boundary</h2>
          <StatusBadge status="Warning" />
        </div>
        <p>Manual approval required: true</p>
        <p>Auto approval: disabled</p>
        <p>Real orders: disabled</p>
        <p>Real money: disabled</p>
        <p>Paper trading only</p>
        <p>Planning only</p>
      </section>
      <div className="grid">
        <MetricCard title="Approval Policy" value={String(policy.reject_by_default ?? true)} description="Reject-by-default policy remains active." status="Warning" />
        <MetricCard title="Approval State Machine" value="DRAFT -> REVIEW" description="Only simulated approval, rejected, or expired states are allowed." />
        <MetricCard title="Reject-by-default Policy" value="On" description="Real order attempts are rejected." status="OK" />
        <MetricCard title="Audit Trail Summary" value={String(audit.event_count ?? 0)} description="Local JSONL planning audit events." />
        <MetricCard title="Missing Production Requirements" value={String(missing.length || 6)} description="Needed before any future broker sandbox." status="Warning" />
        <MetricCard title="Final Verdict" value={String(readiness.verdict ?? 'WARNING')} description="Manual approval planning readiness." status={tone(readiness.verdict)} />
      </div>
      <div className="grid">
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Approval Policy</h2>
            <StatusBadge status="Warning" />
          </div>
          <pre className="codeBlock">{JSON.stringify({ status, policy }, null, 2)}</pre>
        </section>
        <section className="card moduleCard">
          <div className="cardHeader">
            <h2>Audit Trail Summary</h2>
            <StatusBadge status="OK" />
          </div>
          {Object.keys(audit).length ? <pre className="codeBlock">{JSON.stringify(audit, null, 2)}</pre> : <EmptyState title="No approval audit events" description="The page renders safely before approval events exist." />}
        </section>
      </div>
      {warnings.length ? <EmptyState title="Manual approval planning warnings" description={warnings.join(' | ')} /> : null}
    </ProductionShell>
  );
}
