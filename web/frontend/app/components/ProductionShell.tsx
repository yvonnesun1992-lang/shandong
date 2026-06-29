import type { ReactNode } from 'react';

import { EmptyState } from './EmptyState';
import { MetricCard } from './MetricCard';
import { PageHeader } from './PageHeader';

const links = [
  ['Onboarding', '/onboarding'],
  ['Dashboard', '/dashboard'],
  ['Workspace Demo', '/workspace-demo'],
  ['Pricing', '/pricing'],
  ['Strategy', '/strategy'],
  ['Reports', '/reports'],
  ['Risk', '/risk'],
  ['V5 Monitoring', '/v5-monitoring'],
  ['V5 Deployment', '/v5-deployment'],
  ['V5 Live Paper', '/v5-live-paper'],
  ['V5 Live Alpha', '/v5-live-alpha'],
  ['V5 Broker', '/v5-broker'],
  ['V5 Approval', '/v5-approval'],
  ['V5 Sandbox', '/v5-sandbox'],
  ['V5 Sandbox Sim', '/v5-sandbox-sim'],
  ['V5 Sandbox Robustness', '/v5-sandbox-robustness'],
  ['V5 Sandbox Connector', '/v5-sandbox-connector'],
  ['V5 Sandbox Connector Mock', '/v5-sandbox-connector-mock'],
  ['V5 Broker Adapter', '/v5-broker-adapter'],
  ['V5 Sandbox Bridge', '/v5-sandbox-bridge'],
  ['V5 Integration Test', '/v5-integration-test'],
  ['V5 Transition', '/v5-transition'],
  ['V5 Provider Selection', '/v5-provider-selection'],
  ['V5 Provider Onboarding', '/v5-provider-onboarding'],
  ['Login', '/login'],
  ['Admin Console', '/admin'],
  ['Settings', '/settings'],
  ['API Docs', '/api-docs'],
];

type ProductionShellProps = {
  title: string;
  eyebrow: string;
  description?: string;
  activePath?: string;
  children?: ReactNode;
};

export function ProductionShell({ title, eyebrow, description, activePath = '/dashboard', children }: ProductionShellProps) {
  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brandMark">QS</span>
          <div>
            <strong>Shandong SaaS</strong>
            <p>Research control plane</p>
          </div>
        </div>
        <nav className="nav" aria-label="Product navigation">
          {links.map(([label, href]) => (
            <a className={activePath === href ? 'active' : undefined} href={href} key={href}>
              {label}
            </a>
          ))}
        </nav>
        <section className="sidebarPanel">
          <p className="meta">Environment</p>
          <strong>Local / demo environment</strong>
          <p>Research mode only. No broker connection.</p>
        </section>
      </aside>
      <section className="content">
        <PageHeader
          eyebrow={eyebrow}
          title={title}
          description={description ?? 'Unified SaaS research workspace for reports, risk, operations, and platform readiness.'}
          actionLabel="Open Admin Console"
          actionHref="/admin"
        />
        {children ?? (
          <>
            <div className="grid">
              <MetricCard title="Platform Status" value="Ready" description="Local startup and health checks are available." />
              <MetricCard title="Research Mode" value="On" description="No broker connection and no auto trading." />
              <MetricCard title="Billing" value="Mock" description="Mock billing only for product demonstration." status="Warning" />
            </div>
            <EmptyState
              title="No live trading workspace"
              description="This product shell is for research, reporting, and platform readiness demos."
              actionLabel="Review API Docs"
              actionHref="/api-docs"
            />
          </>
        )}
      </section>
    </main>
  );
}
