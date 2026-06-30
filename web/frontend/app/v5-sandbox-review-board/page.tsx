import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Sandbox Review Board', 'Review-board-only packet for future sandbox dry-run readiness.', 'runtime disabled'],
  ['Review Board Charter', 'Purpose, scope, required evidence, required reviewers, approval limitations, and no-execution policy.', 'no execution authority'],
  ['Reviewer Roles', 'Strategy, technical, risk, compliance, security, operations, and emergency reviewer matrix.', 'no role can approve real paths'],
  ['Evidence Review', 'V5.23 through V5.29 evidence, security scan, system doctor, pytest summary, and frontend structure check.', 'not ready'],
  ['Risk Acceptance', 'Credential, sandbox account, provider docs, market data, audit, kill switch, and compliance blockers.', 'no auto acceptance'],
  ['Readiness Score', 'Score is evaluation-only and cannot unlock sandbox access.', 'does not unlock'],
  ['Go / No-Go Decision', 'The V5.30 review board always returns NO_GO.', 'NO_GO'],
  ['Safety Validation', 'Validates no sandbox API, secret read, account read, broker connection, order submission, or real money.', 'paper trading only'],
];

export default function V5SandboxReviewBoardPage() {
  return (
    <ProductionShell
      title="V5 Review Board"
      eyebrow="Sandbox Dry-Run Readiness Review Board"
      description="Review-board-only readiness packet for a future sandbox dry-run, with every runtime and real path locked."
      activePath="/v5-sandbox-review-board"
    >
      <section className="grid">
        <MetricCard title="Decision" value="NO_GO" description="Sandbox dry-run remains blocked in V5.30." />
        <MetricCard title="Review Runtime" value="Disabled" description="No review runtime or reviewer approval path." />
        <MetricCard title="Secret / Account Read" value="Disabled" description="No credential, account, balance, or position read." />
        <MetricCard title="Orders" value="Disabled" description="No real or sandbox order submission." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Review board only</h2>
          </div>
          <StatusBadge status="warning">NO_GO</StatusBadge>
        </div>
        <p className="muted">
          Sandbox dry-run readiness review board only. Review runtime disabled. Reviewer approval disabled. Sandbox API disabled. Secret read disabled. Account read disabled. Broker connected false. Real money disabled. Paper trading only.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Review</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="No sandbox approval"
        description="This page intentionally shows review-board design only. It does not approve sandbox API, read credentials, read accounts, submit orders, or enable real money."
      />
    </ProductionShell>
  );
}
