import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const checks = [
  ['Launcher Verified', 'V5.39 local launcher plan and starter scripts are checked.'],
  ['Backend Smoke', 'FastAPI TestClient verifies local product-home and launcher endpoints.'],
  ['Frontend Smoke', 'Product Home page and navigation files are checked without starting a dev server.'],
  ['API Smoke', 'Product Home and Local Launcher endpoint matrix returns safe success payloads.'],
  ['Log Write', 'Verification logs write only under reports/local_launcher/.'],
  ['Report Generated', 'V5.41 local verification report is generated locally.'],
  ['Safety Boundary', 'Broker, sandbox API, secrets, accounts, orders, and real money remain disabled.'],
];

export default function V5LocalE2EPage() {
  return (
    <ProductionShell
      title="Local E2E Verification"
      eyebrow="V5.41 Local End-to-End Run Verification"
      description="This verifies local run readiness across launcher, backend, frontend, API smoke tests, logs, report generation, and safety boundaries."
      activePath="/v5-local-e2e"
    >
      <section className="grid">
        <MetricCard title="Launcher Verified" value="Ready" description="Local launcher plan stays dry-run and localhost-only." />
        <MetricCard title="Backend Smoke" value="TestClient" description="No long-running backend process is started." />
        <MetricCard title="Frontend Smoke" value="File-level" description="No external network or dev server required." />
        <MetricCard title="Safety" value="Locked" description="No broker, no orders, no real funds." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Scope</p>
            <h2>Local run readiness only</h2>
          </div>
          <StatusBadge status="warning">Verification only</StatusBadge>
        </div>
        <p className="muted">This verifies local run readiness. It does not connect to brokers. It does not submit orders. It does not use real money.</p>
      </section>

      <section className="grid two">
        {checks.map(([title, description]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="ok">Local</StatusBadge>
            </div>
            <p>{description}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="Missing Local Requirements"
        description="Manual browser inspection and packaged desktop installers remain future work. This page intentionally avoids broker, sandbox, secret, account, balance, position, order, and money paths."
      />
    </ProductionShell>
  );
}
