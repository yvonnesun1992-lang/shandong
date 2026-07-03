import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const checks = [
  ['Environment check', 'Python, Node, pnpm, backend entry, frontend entry, and scripts directory.'],
  ['Backend command', 'python -m uvicorn src.api.v2.server:create_v2_api_app --factory --host 127.0.0.1 --port 8000'],
  ['Frontend command', 'cd web/frontend && pnpm dev --hostname 127.0.0.1 --port 3000'],
  ['Browser target', 'http://127.0.0.1:3000'],
  ['Recent launcher logs', 'Local startup events are written to reports/local_launcher/.'],
  ['Safety status', 'Local launcher only, localhost only, paper trading only.'],
];

export default function V5LocalLauncherPage() {
  return (
    <ProductionShell
      title="V5 Local Launcher"
      eyebrow="Local Desktop Launcher"
      description="A local-only startup entry for checking the desktop environment, preparing backend and frontend commands, opening localhost, and keeping all broker, sandbox, account, order, and money paths disabled."
      activePath="/v5-local-launcher"
    >
      <section className="grid">
        <MetricCard title="Launcher Mode" value="Local only" description="Dry-run by default; run mode remains localhost-only." />
        <MetricCard title="Backend" value="127.0.0.1:8000" description="FastAPI factory command generated for local use." />
        <MetricCard title="Frontend" value="127.0.0.1:3000" description="Next.js development command generated for local use." />
        <MetricCard title="Safety" value="Locked" description="No broker, sandbox API, secrets, account reads, or orders." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Usage</p>
            <h2>Desktop startup scripts</h2>
          </div>
          <StatusBadge status="ok">Localhost only</StatusBadge>
        </div>
        <p className="muted">Mac users can double click scripts/start_shandong_mac.command. Windows users can double click scripts/start_shandong_windows.bat.</p>
        <p className="muted">The launcher writes local startup logs under reports/local_launcher/ and never opens external provider URLs.</p>
      </section>

      <section className="grid two">
        {checks.map(([title, description]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="warning">Dry-run safe</StatusBadge>
            </div>
            <p>{description}</p>
          </article>
        ))}
      </section>

      <EmptyState
        title="This is not an installer"
        description="V5.39 is a local launcher layer, not a Mac .app, Windows .exe, broker connector, sandbox API client, credential reader, account reader, or order submission tool."
      />
    </ProductionShell>
  );
}
