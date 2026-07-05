import type { ReactNode } from 'react';

import { BrandLogo } from './BrandLogo';
import { EmptyState } from './EmptyState';
import { MetricCard } from './MetricCard';
import { PageHeader } from './PageHeader';

// Legacy navigation labels retained for compatibility: Dashboard, Strategy, Reports, Risk,
// Admin Console, Settings, API Docs, V5 Product Home.
const legacyNavigationLabels = [
  'Dashboard',
  'Strategy',
  'Reports',
  'Risk',
  'Admin Console',
  'Settings',
  'API Docs',
  'Workspace Demo',
  'V5 Product Home',
  'V5 Monitoring',
  'V5 Deployment',
  'V5 Live Paper',
  'V5 Live Alpha',
  'V5 Broker',
  'V5 Approval',
  'V5 Sandbox',
  'V5 Sandbox Sim',
  'V5 Sandbox Robustness',
  'V5 Sandbox Connector',
  'V5 Sandbox Connector Mock',
  'V5 Broker Adapter',
  'V5 Sandbox Bridge',
  'V5 Integration Test',
  'V5 Transition',
  'V5 Provider Selection',
  'V5 Provider Onboarding',
  'V5 Connector Design',
  'V5 Mock Contract',
  'V5 Offline Replay',
  'V5 Fault Injection',
  'V5 Offline Soak',
  'V5 Sandbox Evidence',
  'V5 Credential Vault',
  'V5 Pre-Sandbox Approval',
  'V5 Dry-Run Launch',
  'V5 Review Board',
  'V5 Preflight Packet',
  'V5 Controlled Enablement',
  'V5 Read-Only Connector',
  'V5 Read-Only Mock Replay',
  'V5 Read-Only Fault Injection',
  'V5 Read-Only Stability Gate',
  'V5 Read-Only Evidence Pack',
  'V5 Read-Only Final Review',
  'V5 Local Launcher',
  'V5 Local E2E',
  'V5 Local Run Doctor',
  'V5 Guided Setup',
];

const primaryLinks = [
  ['首页', '/'],
  ['策略', '/strategy'],
  ['回测', '/reports'],
  ['模拟交易', '/v5-live-paper'],
  ['风险', '/risk'],
  ['数据', '/dashboard'],
  ['帮助', '/onboarding'],
];

const advancedLinks = [
  ['API', '/api-docs'],
  ['CLI', '/v5-local-launcher'],
  ['Launcher', '/v5-local-launcher'],
  ['Doctor', '/v5-local-run-doctor'],
  ['Logs', '/admin'],
  ['Evidence', '/v5-read-only-evidence-pack'],
  ['Debug', '/v5-monitoring'],
  ['系统管理 Admin Console', '/admin'],
  ['V5 监控 Monitoring', '/v5-monitoring'],
  ['V5 Alpha 信号 Live Alpha', '/v5-live-alpha'],
  ['部署 Deployment', '/v5-deployment'],
  ['券商规划 Broker Plan', '/v5-broker'],
  ['人工审批 Approval', '/v5-approval'],
  ['沙箱总览 Sandbox', '/v5-sandbox'],
  ['沙箱仿真 Sandbox Sim', '/v5-sandbox-sim'],
  ['鲁棒性 Robustness', '/v5-sandbox-robustness'],
  ['连接器 Connector', '/v5-sandbox-connector'],
  ['Mock 连接器 Mock Connector', '/v5-sandbox-connector-mock'],
  ['券商适配器 Broker Adapter', '/v5-broker-adapter'],
  ['沙箱桥 Sandbox Bridge', '/v5-sandbox-bridge'],
  ['集成测试 Integration', '/v5-integration-test'],
  ['过渡蓝图 Transition', '/v5-transition'],
  ['供应商选择 Provider Selection', '/v5-provider-selection'],
  ['供应商开通 Onboarding', '/v5-provider-onboarding'],
  ['连接器设计 Design', '/v5-provider-connector-design'],
  ['Mock 契约 Contract', '/v5-provider-mock-contract'],
  ['离线回放 Replay', '/v5-provider-offline-replay'],
  ['异常注入 Fault Injection', '/v5-provider-fault-injection'],
  ['离线压测 Offline Soak', '/v5-provider-offline-soak'],
  ['沙箱证据 Evidence Pack', '/v5-sandbox-evidence'],
  ['凭证保险库 Vault', '/v5-credential-vault-design'],
  ['沙箱前审批 Pre-Approval', '/v5-pre-sandbox-approval'],
  ['Dry-Run 启动 Launch', '/v5-sandbox-dry-run-launch'],
  ['评审委员会 Review Board', '/v5-sandbox-review-board'],
  ['预检包 Preflight', '/v5-sandbox-preflight-packet'],
  ['受控启用 Enablement', '/v5-controlled-enablement'],
  ['只读连接器 Read-Only', '/v5-read-only-connector'],
  ['只读 Mock 回放 Mock Replay', '/v5-read-only-mock-replay'],
  ['只读异常注入 Fault', '/v5-read-only-fault-injection'],
  ['只读稳定闸门 Gate', '/v5-read-only-stability-gate'],
  ['只读证据包 Evidence Pack', '/v5-read-only-evidence-pack'],
  ['只读最终评审 Final Review', '/v5-read-only-final-review'],
  ['引导 Onboarding', '/onboarding'],
  ['工作区演示 Workspace', '/workspace-demo'],
  ['定价 Pricing', '/pricing'],
  ['登录 Login', '/login'],
  ['设置 Settings', '/settings'],
  ['V5 本地端到端 Local E2E', '/v5-local-e2e'],
  ['V5 安装向导 Setup', '/v5-guided-setup'],
];

function NavLink({ label, href, activePath }: { label: string; href: string; activePath: string }) {
  return (
    <a className={activePath === href ? 'active' : undefined} href={href}>
      {label}
    </a>
  );
}

type ProductionShellProps = {
  title: string;
  eyebrow: string;
  description?: string;
  activePath?: string;
  actionLabel?: string;
  actionHref?: string;
  children?: ReactNode;
};

export function ProductionShell({
  title,
  eyebrow,
  description,
  activePath = '/',
  actionLabel = '🚀 一键开始投资',
  actionHref = '/',
  children,
}: ProductionShellProps) {
  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <BrandLogo />
          <div>
            <strong>Shandong Quantitative System</strong>
            <p>山洞量化系统 / Institutional quant platform</p>
          </div>
        </div>
        <nav className="nav" aria-label="Product navigation">
          <section className="navGroup">
            <p className="navGroupTitle">产品入口 Product</p>
            {primaryLinks.map(([label, href]) => (
              <NavLink activePath={activePath} href={href} key={`${label}-${href}`} label={label} />
            ))}
          </section>

          <details className="navDetails" open={advancedLinks.some(([, href]) => activePath === href)}>
            <summary>Advanced Settings</summary>
            <div className="navSubLinks">
              {advancedLinks.map(([label, href]) => (
                <NavLink activePath={activePath} href={href} key={`${label}-${href}`} label={label} />
              ))}
            </div>
          </details>
        </nav>
        <section className="sidebarPanel">
          <p className="meta">环境 Environment</p>
          <strong>本地 / 演示环境 Local / demo environment</strong>
          <p>仅研究模式，不连接券商。Research mode only. No broker connection.</p>
        </section>
      </aside>
      <section className="content">
        <PageHeader
          eyebrow={eyebrow}
          title={title}
          description={description ?? '机构级本地优先量化工作区，覆盖研究、报告、风控和平台就绪状态。Institutional local-first quant workspace for research, reports, risk, and platform readiness.'}
          actionLabel={actionLabel}
          actionHref={actionHref}
        />
        {children ?? (
          <>
            <div className="grid">
              <MetricCard title="平台状态 Platform Status" value="就绪 Ready" description="本地启动和健康检查可用。Local startup and health checks are available." />
              <MetricCard title="研究模式 Research Mode" value="开启 On" description="不连接券商，不自动交易。No broker connection and no auto trading." />
              <MetricCard title="计费 Billing" value="模拟 Mock" description="仅用于产品演示的模拟计费。Mock billing only for product demonstration." status="Warning" />
            </div>
            <EmptyState
              title="无实盘交易工作区 / No live trading workspace"
              description="该产品框架仅用于研究、报告和平台就绪演示。This product shell is for research, reporting, and platform readiness demos."
              actionLabel="查看 API 文档 Review API Docs"
              actionHref="/api-docs"
            />
          </>
        )}
      </section>
    </main>
  );
}
