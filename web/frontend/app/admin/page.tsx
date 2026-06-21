const statusCards = [
  ['System Overview', 'OK', 'Runtime shell, health checks, and release status are visible.'],
  ['API Health', 'OK', 'FastAPI v2 service and standard response layer are monitored.'],
  ['Database', 'OK', 'SQLite local storage and migration readiness are summarized.'],
  ['Auth & Security', 'Warning', 'Local mode is allowed for development; production requires hardened auth.'],
  ['Workspace', 'OK', 'Tenant isolation status and default workspace readiness are tracked.'],
  ['Plan / Quota', 'OK', 'Mock plan and usage limit health are visible without real payments.'],
  ['Deployment', 'OK', 'Startup check, readiness, and liveness are represented.'],
  ['Release Candidate', 'OK', 'V2 freeze and integration QA status are surfaced.'],
];

function statusClass(status: string) {
  return `badge badge-${status.toLowerCase()}`;
}

export default function AdminConsolePage() {
  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">Shandong SaaS</div>
        <nav className="nav">
          <a href="/dashboard">Dashboard</a>
          <a href="/strategy">Strategy</a>
          <a href="/reports">Reports</a>
          <a href="/risk">Risk</a>
          <a href="/settings">Settings</a>
          <a href="/admin">Admin Console</a>
          <a href="/api-docs">API Docs</a>
        </nav>
      </aside>
      <section className="content">
        <p className="eyebrow">Product Control Center</p>
        <h1>Admin Console</h1>
        <div className="grid">
          {statusCards.map(([title, status, description]) => (
            <section className="card" key={title}>
              <div className="cardHeader">
                <h2>{title}</h2>
                <span className={statusClass(status)}>{status}</span>
              </div>
              <p className="muted">{description}</p>
            </section>
          ))}
        </div>
      </section>
    </main>
  );
}
