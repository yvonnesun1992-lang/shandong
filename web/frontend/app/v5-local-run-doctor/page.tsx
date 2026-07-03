import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const guideItems = [
  ['Python status', 'Checks whether Python or Python 3 is available.'],
  ['Node status', 'Explains whether the frontend can run at all.'],
  ['pnpm status', 'Shows whether frontend dependency commands are available.'],
  ['Frontend dependency status', 'Points to pnpm install when node_modules is missing.'],
  ['Backend status', 'Uses local TestClient checks without starting a long-running server.'],
  ['Frontend port 3000 status', 'Checks only 127.0.0.1:3000.'],
  ['Backend port 8000 status', 'Checks only 127.0.0.1:8000.'],
];

export default function V5LocalRunDoctorPage() {
  return (
    <ProductionShell
      title="Local Run Doctor"
      eyebrow="V5.42 Local Run Doctor"
      description="Why 127.0.0.1:3000 may not open, with safe local diagnostics and copyable next steps."
      activePath="/v5-local-run-doctor"
    >
      <section className="grid">
        <MetricCard title="Python" value="Checked" description="Command availability only." />
        <MetricCard title="Node / pnpm" value="Checked" description="No automatic install is performed." status="Warning" />
        <MetricCard title="Ports" value="3000 / 8000" description="Localhost-only socket checks." />
        <MetricCard title="Safety" value="Locked" description="No broker, no orders, no real funds." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Diagnosis</p>
            <h2>Why 127.0.0.1:3000 may not open</h2>
          </div>
          <StatusBadge status="warning">Manual fix guide</StatusBadge>
        </div>
        <p className="muted">This doctor does not install anything automatically. It does not connect to brokers. It does not submit orders. It does not use real money.</p>
      </section>

      <section className="grid two">
        {guideItems.map(([title, description]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="ok">Local</StatusBadge>
            </div>
            <p>{description}</p>
          </article>
        ))}
      </section>

      <section className="grid two">
        <article className="card">
          <h3>Mac fix guide</h3>
          <p>Install Node.js LTS if missing, reopen Terminal, run the local verification, start the launcher, then open http://127.0.0.1:3000.</p>
        </article>
        <article className="card">
          <h3>Windows fix guide</h3>
          <p>Install Node.js LTS if missing, reopen PowerShell, run the local verification, start the launcher, then open http://127.0.0.1:3000.</p>
        </article>
      </section>

      <EmptyState
        title="Recommended next steps"
        description="Use the generated CLI report for exact local commands. The doctor only diagnoses local run readiness and keeps broker, sandbox, credential, account, balance, position, order, and money paths disabled."
      />
    </ProductionShell>
  );
}
