import { EmptyState } from './components/EmptyState';
import { MetricCard } from './components/MetricCard';
import { ProductionShell } from './components/ProductionShell';
import { StatusBadge } from './components/StatusBadge';

const featureCards = [
  ['Research', '/strategy', 'Generate and review local quant research reports.'],
  ['Backtest', '/reports', 'Open backtest and performance report workflows.'],
  ['Paper Trading', '/v5-live-paper', 'Review paper-only runtime and monitoring status.'],
  ['Risk Monitor', '/risk', 'Inspect risk controls and disabled real-trading paths.'],
  ['Logs', '/admin', 'Review local operations and system summaries.'],
  ['Local Launcher', '/v5-local-launcher', 'Start with the V5.39 localhost-only launcher.'],
];

const recentActivity = [
  ['Latest local report', 'Open reports for generated V5 summaries and validation artifacts.'],
  ['Launcher logs', 'Review reports/local_launcher after using the desktop starter scripts.'],
  ['Workflow runs', 'Inspect local workflow run records when available.'],
];

const nextSteps = [
  ['Run Local Launcher', '/v5-local-launcher'],
  ['Check System Health', '/admin'],
  ['Open Paper Trading', '/v5-live-paper'],
  ['Review Backtest', '/reports'],
];

export default function HomePage() {
  return (
    <ProductionShell
      title="Shandong Quant System"
      eyebrow="Product Home Dashboard"
      description="Local-first paper trading and research dashboard"
      activePath="/"
    >
      <section className="grid">
        <MetricCard title="System Health" value="Ready" description="Local backend, frontend, launcher, and reports are summarized here." />
        <MetricCard title="Local Launcher" value="Available" description="Use the V5.39 launcher for localhost startup checks." />
        <MetricCard title="Paper Trading" value="Paper only" description="Research and paper workflows only; no live trading." status="Warning" />
        <MetricCard title="Safety Boundary" value="Locked" description="No broker, no sandbox API, no account reads, no order submission." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Current status</p>
            <h2>Local-first product overview</h2>
          </div>
          <StatusBadge status="ok">Localhost only</StatusBadge>
        </div>
        <div className="grid two">
          <article className="card">
            <h3>Current mode</h3>
            <p>Current system remains Paper Trading only.</p>
            <p className="muted">Broker disconnected. Sandbox API disabled. Order submission disabled. Real money disabled.</p>
          </article>
          <article className="card">
            <h3>Safety boundary</h3>
            <p>No real broker connected. No real money. No order submission.</p>
            <p className="muted">The dashboard does not read secrets, accounts, balances, positions, or provider payloads.</p>
          </article>
        </div>
      </section>

      <section className="grid two">
        {featureCards.map(([title, href, description]) => (
          <a className="card linkCard" href={href} key={href}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Local</StatusBadge>
            </div>
            <p>{description}</p>
          </a>
        ))}
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="meta">Recent activity</p>
              <h2>Local records</h2>
            </div>
            <StatusBadge status="warning">Summary</StatusBadge>
          </div>
          {recentActivity.map(([title, description]) => (
            <div className="listRow" key={title}>
              <strong>{title}</strong>
              <span>{description}</span>
            </div>
          ))}
        </article>
        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="meta">Next steps</p>
              <h2>Recommended actions</h2>
            </div>
            <StatusBadge status="ok">Guided</StatusBadge>
          </div>
          {nextSteps.map(([title, href]) => (
            <a className="listRow" href={href} key={href}>
              <strong>{title}</strong>
              <span>Open</span>
            </a>
          ))}
        </article>
      </section>

      <EmptyState
        title="No live broker workspace"
        description="This Product Home Dashboard is intentionally read-only and local-first. It does not connect to brokers, sandbox APIs, accounts, balances, positions, orders, or real funds."
      />
    </ProductionShell>
  );
}
