import { EmptyState } from '../components/EmptyState';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const cards = [
  ['Missing Requirements', 'Shows Node, npm, pnpm, frontend dependencies, backend process, and frontend process status.'],
  ['Mac Setup Steps', 'Step-by-step Terminal instructions with copyable commands.'],
  ['Windows Setup Steps', 'Step-by-step PowerShell instructions with copyable commands.'],
  ['Copy Commands', 'Commands are shown for the user to copy; the wizard does not run them.'],
  ['Plain Language Explanation', 'Explains frontend 3000, backend 8000, Node.js, pnpm, and what to do next.'],
  ['Safety Boundary', 'Broker, sandbox, credential, account, order, and real money paths stay disabled.'],
];

export default function V5GuidedSetupPage() {
  return (
    <ProductionShell
      title="Guided Local Setup Wizard"
      eyebrow="V5.43 Guided Local Setup Wizard"
      description="A friendly setup guide for opening the local product home at 127.0.0.1:3000."
      activePath="/v5-guided-setup"
    >
      <section className="grid">
        <MetricCard title="Current blocker" value="Node / frontend" description="The wizard explains why 3000 may not open." status="Warning" />
        <MetricCard title="Auto install" value="Off" description="这个向导不会自动安装任何东西。" />
        <MetricCard title="Orders" value="Blocked" description="这个向导不会连接券商或提交订单。" />
        <MetricCard title="Local only" value="127.0.0.1" description="No external network automation." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">Plain language</p>
            <h2>如果 127.0.0.1:3000 打不开，通常是前端没有启动</h2>
          </div>
          <StatusBadge status="warning">Manual steps only</StatusBadge>
        </div>
        <p className="muted">Node.js 是运行网页前端需要的工具。pnpm 是安装前端依赖需要的工具。这个向导不会自动安装任何东西。这个向导不会连接券商或提交订单。</p>
      </section>

      <section className="grid two">
        {cards.map(([title, description]) => (
          <article className="card" key={title}>
            <div className="rowBetween">
              <h3>{title}</h3>
              <StatusBadge status="ok">Guide</StatusBadge>
            </div>
            <p>{description}</p>
          </article>
        ))}
      </section>

      <section className="grid two">
        <article className="card">
          <h3>What to do next</h3>
          <p>Install Node.js LTS manually if it is missing, reopen your terminal, install pnpm if needed, install frontend dependencies, then start backend and frontend in separate terminals.</p>
        </article>
        <article className="card">
          <h3>Command preview</h3>
          <p>Run the guided setup CLI for exact copy commands: python scripts/run_v543_guided_setup_wizard.py --check commands.</p>
        </article>
      </section>

      <EmptyState
        title="This is a setup guide, not an installer"
        description="The wizard provides readable steps and command blocks. It does not modify PATH, request admin permissions, start services, access credentials, connect brokers, or submit orders."
      />
    </ProductionShell>
  );
}
