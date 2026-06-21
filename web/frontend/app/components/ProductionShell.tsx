import { ChartCard } from './ChartCard';

const links = [
  ['Login', '/login'],
  ['Dashboard', '/dashboard'],
  ['Strategy', '/strategy'],
  ['Reports', '/reports'],
  ['Risk', '/risk'],
  ['Settings', '/settings'],
  ['Admin Console', '/admin'],
  ['API Docs', '/api-docs'],
];

export function ProductionShell({ title, eyebrow }: { title: string; eyebrow: string }) {
  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">Shandong SaaS</div>
        <nav className="nav">
          {links.map(([label, href]) => (
            <a href={href} key={href}>{label}</a>
          ))}
        </nav>
      </aside>
      <section className="content">
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <div className="grid">
          <section className="card">
            <h2>System Health</h2>
            <p className="metric">99.9%</p>
            <p className="muted">Production readiness shell</p>
          </section>
          <section className="card">
            <h2>API Latency</h2>
            <p className="metric">24ms</p>
            <p className="muted">Mock monitoring metric</p>
          </section>
          <section className="card">
            <h2>Plan</h2>
            <p className="metric">Pro</p>
            <p className="muted">Simulated billing tier</p>
          </section>
          <ChartCard />
        </div>
      </section>
    </main>
  );
}
