import { EmptyState } from './components/EmptyState';
import { BrandLogo } from './components/BrandLogo';
import { MetricCard } from './components/MetricCard';
import { ProductionShell } from './components/ProductionShell';
import { StatusBadge } from './components/StatusBadge';

// Legacy V5.40 product-home labels retained for compatibility:
// Shandong Quant System; Local-first paper trading and research dashboard.
const featureCards = [
  ['研究 Research', '/strategy', '生成并查看本地量化研究报告。Generate and review local quant research reports.'],
  ['回测 Backtest', '/reports', '查看回测与绩效报告流程。Open backtest and performance report workflows.'],
  ['模拟交易 Paper Trading', '/v5-live-paper', '查看仅模拟交易的运行与监控状态。Review paper-only runtime and monitoring status.'],
  ['风险监控 Risk Monitor', '/risk', '检查风控与禁用的真实交易路径。Inspect risk controls and disabled real-trading paths.'],
  ['日志 Logs', '/admin', '查看本地运维与系统汇总。Review local operations and system summaries.'],
  ['本地启动器 Local Launcher', '/v5-local-launcher', '从 V5.39 localhost-only 启动器开始。Start with the V5.39 localhost-only launcher.'],
];

const recentActivity = [
  ['最新本地报告 Latest local report', '打开报告查看已生成的 V5 摘要和验证材料。Open reports for generated V5 summaries and validation artifacts.'],
  ['启动器日志 Launcher logs', '使用桌面启动脚本后查看 reports/local_launcher。Review reports/local_launcher after using the desktop starter scripts.'],
  ['工作流记录 Workflow runs', '如有本地工作流记录，可在这里检查。Inspect local workflow run records when available.'],
];

const nextSteps = [
  ['运行本地启动器 Run Local Launcher', '/v5-local-launcher'],
  ['检查系统健康 Check System Health', '/admin'],
  ['打开模拟交易 Open Paper Trading', '/v5-live-paper'],
  ['查看回测 Review Backtest', '/reports'],
];

export default function HomePage() {
  return (
    <ProductionShell
      title="Shandong Quantitative System"
      eyebrow="山洞量化系统 / Institutional Quant Platform"
      description="机构级本地优先量化平台。Institutional-grade local-first quant platform."
      activePath="/"
    >
      <section className="brandShowcase">
        <BrandLogo size="large" />
        <div>
          <p className="eyebrow">Brand System V5.44</p>
          <h2>山洞量化系统 / Shandong Quantitative System</h2>
          <p className="muted">深蓝 + 金色山峰 K 线品牌体系，面向本地研究、模拟交易、风控和运行诊断。</p>
        </div>
      </section>

      <section className="grid">
        <MetricCard title="系统健康 System Health" value="就绪 Ready" description="这里汇总本地后端、前端、启动器和报告状态。Local backend, frontend, launcher, and reports are summarized here." />
        <MetricCard title="本地启动器 Local Launcher" value="可用 Available" description="用于 localhost 启动检查的 V5.39 启动器已可用。Use the V5.39 launcher for localhost startup checks." />
        <MetricCard title="模拟交易 Paper Trading" value="仅模拟 Paper only" description="仅支持研究和模拟交易流程；不进行实盘交易。Research and paper workflows only; no live trading." status="Warning" />
        <MetricCard title="安全边界 Safety Boundary" value="已锁定 Locked" description="不连接券商、不启用 sandbox API、不读取账户、不提交订单。No broker, no sandbox API, no account reads, no order submission." />
      </section>

      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">当前状态 Current status</p>
            <h2>本地优先产品总览 / Local-first product overview</h2>
          </div>
          <StatusBadge status="ok">仅本地 Localhost only</StatusBadge>
        </div>
        <div className="grid two">
          <article className="card">
            <h3>当前模式 / Current mode</h3>
            <p>当前系统保持仅模拟交易。Current system remains Paper Trading only.</p>
            <p className="muted">券商未连接，Sandbox API 禁用，订单提交禁用，真实资金禁用。Broker disconnected. Sandbox API disabled. Order submission disabled. Real money disabled.</p>
          </article>
          <article className="card">
            <h3>安全边界 / Safety boundary</h3>
            <p>不连接真实券商，不使用真实资金，不提交订单。No real broker connected. No real money. No order submission.</p>
            <p className="muted">看板不会读取密钥、账户、余额、持仓或原始供应商数据。The dashboard does not read secrets, accounts, balances, positions, or provider payloads.</p>
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
              <p className="meta">最近活动 Recent activity</p>
              <h2>本地记录 / Local records</h2>
            </div>
            <StatusBadge status="warning">摘要 Summary</StatusBadge>
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
              <p className="meta">下一步 Next steps</p>
              <h2>推荐操作 / Recommended actions</h2>
            </div>
            <StatusBadge status="ok">已引导 Guided</StatusBadge>
          </div>
          {nextSteps.map(([title, href]) => (
            <a className="listRow" href={href} key={href}>
              <strong>{title}</strong>
              <span>打开 Open</span>
            </a>
          ))}
        </article>
      </section>

      <EmptyState
        title="无实盘券商工作区 / No live broker workspace"
        description="本产品首页刻意保持只读和本地优先：不连接券商、Sandbox API、账户、余额、持仓、订单或真实资金。This Product Home Dashboard is intentionally read-only and local-first. It does not connect to brokers, sandbox APIs, accounts, balances, positions, orders, or real funds."
      />
    </ProductionShell>
  );
}
