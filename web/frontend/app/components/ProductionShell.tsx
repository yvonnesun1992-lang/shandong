import type { ReactNode } from 'react';

import { EmptyState } from './EmptyState';
import { MetricCard } from './MetricCard';
import { PageHeader } from './PageHeader';

const links = [
  ['Home', '/'],
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
  ['V5 Connector Design', '/v5-provider-connector-design'],
  ['V5 Mock Contract', '/v5-provider-mock-contract'],
  ['V5 Offline Replay', '/v5-provider-offline-replay'],
  ['V5 Fault Injection', '/v5-provider-fault-injection'],
  ['V5 Offline Soak', '/v5-provider-offline-soak'],
  ['V5 Sandbox Evidence', '/v5-sandbox-evidence'],
  ['V5 Credential Vault', '/v5-credential-vault-design'],
  ['V5 Pre-Sandbox Approval', '/v5-pre-sandbox-approval'],
  ['V5 Dry-Run Launch', '/v5-sandbox-dry-run-launch'],
  ['V5 Review Board', '/v5-sandbox-review-board'],
  ['V5 Preflight Packet', '/v5-sandbox-preflight-packet'],
  ['V5 Controlled Enablement', '/v5-controlled-enablement'],
  ['V5 Read-Only Connector', '/v5-read-only-connector'],
  ['V5 Read-Only Mock Replay', '/v5-read-only-mock-replay'],
  ['V5 Read-Only Fault Injection', '/v5-read-only-fault-injection'],
  ['V5 Read-Only Stability Gate', '/v5-read-only-stability-gate'],
  ['V5 Read-Only Evidence Pack', '/v5-read-only-evidence-pack'],
  ['V5 Read-Only Final Review', '/v5-read-only-final-review'],
  ['V5 Local Launcher', '/v5-local-launcher'],
  ['V5 Local E2E', '/v5-local-e2e'],
  ['V5 Product Home', '/'],
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
