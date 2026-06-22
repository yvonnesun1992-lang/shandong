type WorkspaceDemoCardProps = {
  workspaceName: string;
  plan: string;
  role: string;
  quota: string;
  usage: string;
  reports: string;
  status: string;
};

export function WorkspaceDemoCard({ workspaceName, plan, role, quota, usage, reports, status }: WorkspaceDemoCardProps) {
  return (
    <section className="card">
      <div className="cardHeader">
        <h2>Workspace name</h2>
        <span className="badge badge-ok">{status}</span>
      </div>
      <p className="moduleMetric">{workspaceName}</p>
      <div className="miniGrid">
        <div>
          <strong>Plan</strong>
          <span>{plan}</span>
        </div>
        <div>
          <strong>Role</strong>
          <span>{role}</span>
        </div>
        <div>
          <strong>Quota</strong>
          <span>{quota}</span>
        </div>
        <div>
          <strong>Usage</strong>
          <span>{usage}</span>
        </div>
        <div>
          <strong>Reports</strong>
          <span>{reports}</span>
        </div>
        <div>
          <strong>Status</strong>
          <span>{status}</span>
        </div>
      </div>
    </section>
  );
}
