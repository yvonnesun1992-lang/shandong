import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { WorkspaceDemoCard } from '../components/WorkspaceDemoCard';

const roles = ['admin', 'user', 'viewer'];
const reports = ['Strategy research report', 'Risk review', 'Release candidate summary'];

export default function WorkspaceDemoPage() {
  return (
    <ProductionShell
      title="Workspace Demo"
      eyebrow="Customer Workspace Demo Flow"
      description="A safe tenant-style walkthrough showing workspace, role, quota, usage, reports, and admin relationships."
      activePath="/workspace-demo"
    >
      <section className="card">
        <div className="cardHeader">
          <h2>Demo Workspace Overview</h2>
          <span className="badge badge-warning">Demo workspace only</span>
        </div>
        <p className="muted">No real customer connected. No real billing. No broker connection. No auto trading.</p>
      </section>
      <WorkspaceDemoCard
        workspaceName="Demo Workspace"
        plan="demo"
        role="admin"
        quota="demo only"
        usage="safe sample usage"
        reports="sample research reports"
        status="available"
      />
      <div className="summaryStrip">
        <MetricCard title="Workspace member roles" value="3 roles" description={roles.join(' / ')} />
        <MetricCard title="Quota snapshot" value="Demo" description="Quota is illustrative and not tied to real billing." status="Warning" />
        <MetricCard title="Usage summary" value="Sample" description="Usage is safe fallback data for product demos." />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>Research reports overview</h2>
          <span className="badge badge-ok">Sample data</span>
        </div>
        <div className="grid">
          {reports.map((report) => (
            <div className="card" key={report}>
              <h2>{report}</h2>
              <p className="muted">Demo-only report context for explaining workspace relationships.</p>
            </div>
          ))}
        </div>
      </section>
      <section className="card heroPanel">
        <div>
          <p className="eyebrow">Safety boundaries</p>
          <h2>Demo workspace only</h2>
          <p className="muted">No real customer connected. No real billing. No broker connection. No auto trading.</p>
        </div>
        <a className="button" href="/admin">
          Admin Console
        </a>
      </section>
      <EmptyState
        title="Next actions"
        description="Open Admin Console to connect this workspace story to readiness, quota, billing, and safety modules."
        actionLabel="Open Admin Console"
        actionHref="/admin"
      />
    </ProductionShell>
  );
}
