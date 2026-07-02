import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const sections = [
  ['Final Review Charter', 'Defines the review-only authority and explicitly excludes sandbox API, secrets, accounts, orders, and funds.', 'charter'],
  ['Reviewer Roles', 'Lists reviewers and confirms no role can approve or override real path blockers.', 'roles'],
  ['Evidence Review', 'Reviews V5.34 mock replay, V5.35 fault injection, V5.36 stability gate, and V5.37 evidence pack.', 'evidence'],
  ['Risk Acceptance', 'Keeps live credential, account, provider, audit, rollback, and compliance risks blocked.', 'blocked'],
  ['Missing Requirements', 'Tracks missing production requirements before any future real read-only sandbox work.', 'gaps'],
  ['Final Decision', 'Keeps the board decision at READ_ONLY_FINAL_REVIEW_ONLY.', 'review only'],
];

export default function V5ReadOnlyFinalReviewPage() {
  return (
    <ProductionShell
      title="V5 Read-Only Final Review"
      eyebrow="Sandbox Read-Only Connector Final Review Board"
      description="Final review only: reviews local evidence and open risks, while keeping connector access, sandbox API, secrets, account reads, order paths, and real money disabled."
      activePath="/v5-read-only-final-review"
    >
      <section className="grid">
        <MetricCard title="Mode" value="Final review only" description="Review board package without execution authority." />
        <MetricCard title="Decision" value="Review only" description="READ_ONLY_FINAL_REVIEW_ONLY by design." />
        <MetricCard title="Connector Access" value="Disallowed" description="No reviewer can unlock read-only connector access." />
        <MetricCard title="Risks" value="Blocked" description="Live sandbox requirements remain missing." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Boundary</p>
            <h2>Read-only final review board</h2>
          </div>
          <StatusBadge status="warning">Review only</StatusBadge>
        </div>
        <p className="muted">
          V5.38 reviews V5.34 through V5.37 local evidence. Final review runtime, sandbox API, credential access, account reads, balance reads, position reads, order preview, order submission, broker connection, and real money remain disabled.
        </p>
      </section>

      <section className="grid two">
        {sections.map(([title, description, note]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Board</StatusBadge>
            </div>
            <p>{description}</p>
            <p className="meta">{note}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="Review cannot unlock access"
        description="This page intentionally shows final review status only. It does not connect to providers, read secrets, read accounts, read balances, read positions, preview orders, submit orders, or enable real funds."
      />
    </ProductionShell>
  );
}
