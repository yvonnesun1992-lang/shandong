import { BrandLogo } from './components/BrandLogo';
import { MetricCard } from './components/MetricCard';
import { ProductionShell } from './components/ProductionShell';
import { StatusBadge } from './components/StatusBadge';

// Legacy V5.40 product-home labels retained for compatibility:
// Shandong Quant System; Local-first paper trading and research dashboard.

const productMetrics = [
  ['今日收益', '+0.86%', '模拟组合今日表现。Paper portfolio daily return.', 'OK'],
  ['本周收益', '+2.41%', '近 5 个交易日累计表现。Five-session simulated return.', 'OK'],
  ['月度收益', '+6.80%', '本月策略收益估算。Month-to-date strategy return.', 'OK'],
  ['最大回撤', '-3.20%', '当前模拟组合最大回撤。Current simulated max drawdown.', 'Warning'],
  ['当前仓位', '68%', '模拟组合风险暴露。Paper exposure only.', 'Warning'],
  ['市场状态', '震荡偏多', 'Regime: sideways with positive momentum.', 'OK'],
] as const;

const activityRows = [
  ['策略回测成功', '小市值动量策略完成最近样本回测。'],
  ['模拟交易运行中', 'Paper Trading Mode 持续记录本地模拟组合。'],
  ['风险检查通过', 'Risk Control Enabled，最大回撤和仓位限制正常。'],
];

const curvePoints = [
  [16, 24],
  [28, 34],
  [42, 38],
  [56, 52],
  [70, 63],
  [84, 78],
] as const;

export default function HomePage() {
  return (
    <ProductionShell
      title="Shandong Quantitative System"
      eyebrow="📊 Institutional Quant Investing Platform"
      description="面向普通用户的一键量化投资产品原型。Local-first quant investing experience for research and paper trading."
      activePath="/"
      actionLabel="🚀 一键开始投资"
      actionHref="#one-click-investment"
    >
      <section className="productHero">
        <div className="productHeroCopy">
          <div className="productStatusRow">
            <StatusBadge status="OK" />
            <span>Paper Trading Mode</span>
            <span>Risk Control Enabled</span>
            <span>Local System Running</span>
          </div>
          <h2>普通人可用的量化投资驾驶舱</h2>
          <p>
            系统自动推荐策略、执行回测、进入模拟交易，并用简单的收益和风险指标展示结果。
            No real broker connected. No real money. No order submission.
          </p>
          <div className="ctaRow" id="one-click-investment">
            <a className="button button-large" href="#recommended-strategy">
              🚀 一键开始投资
            </a>
            <a className="button button-secondary" href="/strategies">
              📈 查看策略表现
            </a>
            <a className="button button-secondary" href="/reports">
              🔬 运行回测
            </a>
          </div>
        </div>
        <div className="heroLogoPanel">
          <BrandLogo size="large" />
          <strong>山洞量化系统</strong>
          <span>Institutional-grade local-first quant platform</span>
        </div>
      </section>

      <section className="grid productMetrics">
        {productMetrics.map(([title, value, description, status]) => (
          <MetricCard title={title} value={value} description={description} status={status} key={title} />
        ))}
      </section>

      <section className="grid two">
        <article className="panel" id="recommended-strategy">
          <div className="panelHeader">
            <div>
              <p className="meta">📌 推荐策略（系统自动生成）</p>
              <h2>小市值动量策略</h2>
            </div>
            <StatusBadge status="OK" />
          </div>
          <div className="recommendationGrid">
            <div>
              <span>适配市场</span>
              <strong>震荡偏多</strong>
            </div>
            <div>
              <span>风险等级</span>
              <strong>中</strong>
            </div>
            <div>
              <span>推荐操作</span>
              <strong>✔ 可直接运行</strong>
            </div>
          </div>
          <p className="muted">
            一键流程会先运行回测，再进入模拟交易展示，不会提交真实订单，也不会读取真实账户。
          </p>
        </article>

        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="meta">收益曲线</p>
              <h2>策略收益线 vs 基准收益线</h2>
            </div>
            <StatusBadge status="Warning" />
          </div>
          <div className="performanceChart" aria-label="策略收益线和基准收益线">
            {curvePoints.map(([strategy, benchmark], index) => (
              <div className="curveColumn" key={index}>
                <span className="strategyBar" style={{ height: `${strategy}%` }} />
                <span className="benchmarkBar" style={{ height: `${benchmark}%` }} />
              </div>
            ))}
          </div>
          <div className="legendRow">
            <span><i className="legendGold" />策略收益线</span>
            <span><i className="legendBlue" />基准收益线</span>
          </div>
        </article>
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="meta">最近运行记录</p>
              <h2>无需理解量化，也能看懂运行结果</h2>
            </div>
            <StatusBadge status="OK" />
          </div>
          {activityRows.map(([title, description]) => (
            <div className="listRow" key={title}>
              <strong>{title}</strong>
              <span>{description}</span>
            </div>
          ))}
        </article>

        <article className="panel safetyPanel">
          <div className="panelHeader">
            <div>
              <p className="meta">安全提示</p>
              <h2>⚠ 当前为模拟交易环境</h2>
            </div>
            <StatusBadge status="Warning" />
          </div>
          <ul className="safetyList">
            <li>❌ 无真实资金</li>
            <li>❌ 无真实交易</li>
            <li>❌ 不连接券商</li>
            <li>✔ 仅用于研究、回测和模拟交易展示</li>
          </ul>
        </article>
      </section>
    </ProductionShell>
  );
}
