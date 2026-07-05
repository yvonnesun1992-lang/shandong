import { ProductionShell } from '../../components/ProductionShell';
import { StatusBadge } from '../../components/StatusBadge';

type BacktestResultPageProps = {
  params: {
    strategyId: string;
  };
};

const metricCards = [
  ['策略收益', '+18.6%', '策略在回测期间赚了多少。'],
  ['基准收益', '+11.2%', '同期市场指数涨了多少。'],
  ['超额收益', '+7.4%', '策略比市场多赚或少赚多少。'],
  ['年化收益', '+8.1%', '换算成年平均表现。'],
  ['最大回撤', '-11.8%', '最差的时候亏了多少。'],
  ['胜率', '57%', '赚钱天数或交易次数占比。'],
  ['盈亏比', '1.32', '平均赚钱和平均亏钱幅度比较。'],
  ['夏普比率', '1.18', '收益是否值得承担风险。'],
] as const;

const advancedMetrics = ['Alpha +4.1%', 'Beta 0.83', '信息比率 0.74', '索提诺比率 1.36', '波动率 15.8%', '基准波动率 17.1%'];
const curvePoints = [16, 28, 36, 51, 64, 82] as const;
const benchmarkPoints = [14, 23, 31, 42, 51, 66] as const;
const excessBars = [22, -14, 31, 8, -7, 38] as const;
const tradeBars = [32, -18, 27, 12, -24, 30] as const;

export default function BacktestResultPage({ params }: BacktestResultPageProps) {
  return (
    <ProductionShell
      title="回测结果"
      eyebrow="Backtest Result Dashboard"
      description="用普通投资者能看懂的方式，判断这个策略是否值得继续观察。"
      activePath="/backtest/small_cap_momentum"
      actionLabel="加入模拟交易"
      actionHref="/v5-live-paper"
    >
      <section className="panel">
        <div className="panelHeader">
          <div>
            <p className="meta">策略信息栏</p>
            <h2>小市值动量策略</h2>
          </div>
          <StatusBadge status="OK" />
        </div>
        <div className="infoGrid">
          <div><strong>回测区间</strong><span>2023-01-03 至 2025-12-31</span></div>
          <div><strong>初始资金</strong><span>100,000 模拟资金</span></div>
          <div><strong>调仓频率</strong><span>每周</span></div>
          <div><strong>基准指数</strong><span>沪深300</span></div>
          <div><strong>回测状态</strong><span>已完成</span></div>
          <div><strong>交易模式</strong><span>模拟环境 / Paper Trading</span></div>
        </div>
      </section>

      <section className="grid two">
        <article className="panel conclusionCard">
          <div className="panelHeader">
            <div>
              <p className="meta">系统结论</p>
              <h2>策略表现较好，可以考虑进入模拟交易观察。</h2>
            </div>
            <StatusBadge status="Warning" />
          </div>
          <p className="muted">本次回测跑赢基准，但最大回撤为中等水平。普通投资者应先观察模拟交易，不建议理解为真实收益承诺。</p>
        </article>
        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="meta">操作按钮区</p>
              <h2>下一步建议</h2>
            </div>
            <StatusBadge status="OK" />
          </div>
          <div className="ctaRow">
            <a className="button" href={`/backtest/${params.strategyId}`}>重新回测</a>
            <a className="button button-secondary" href="/strategies">换一个策略</a>
            <a className="button button-secondary" href="/v5-live-paper">加入模拟交易</a>
            <a className="button button-secondary" href="#export">导出报告</a>
            <a className="button button-secondary" href="#attribution">查看收益来源</a>
          </div>
        </article>
      </section>

      <section>
        <div className="panelHeader">
          <div>
            <p className="meta">核心指标</p>
            <h2>先看收益，再看风险</h2>
          </div>
        </div>
        <div className="grid backtestMetricGrid">
          {metricCards.map(([label, value, explanation]) => (
            <article className="metricCard card" key={label}>
              <div className="cardHeader">
                <h2>{label}</h2>
                <span className={value.startsWith('-') ? 'badge badge-warning' : 'badge badge-ok'}>{value}</span>
              </div>
              <p className="muted">{explanation}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="meta">收益曲线</p>
              <h2>策略收益 / 基准收益 / 超额收益</h2>
            </div>
            <StatusBadge status="OK" />
          </div>
          <div className="performanceChart" aria-label="收益曲线">
            {curvePoints.map((strategy, index) => (
              <div className="curveColumn" key={index}>
                <span className="strategyBar" style={{ height: `${strategy}%` }} />
                <span className="benchmarkBar" style={{ height: `${benchmarkPoints[index]}%` }} />
              </div>
            ))}
          </div>
          <p className="muted">蓝线高于基准线，代表策略跑赢市场；低于基准线，代表策略跑输市场。</p>
        </article>

        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="meta">每日跑赢 / 跑输图</p>
              <h2>Daily Excess Return</h2>
            </div>
            <StatusBadge status="Warning" />
          </div>
          <div className="barChart">
            {excessBars.map((value, index) => (
              <span className={value >= 0 ? 'positiveBar' : 'negativeBar'} style={{ height: `${Math.abs(value) + 24}px` }} key={index} />
            ))}
          </div>
        </article>
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="meta">每日交易动作图</p>
              <h2>Buy / Sell / Net Amount</h2>
            </div>
            <StatusBadge status="OK" />
          </div>
          <div className="barChart">
            {tradeBars.map((value, index) => (
              <span className={value >= 0 ? 'positiveBar' : 'negativeBar'} style={{ height: `${Math.abs(value) + 20}px` }} key={index} />
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="meta">风险分析</p>
              <h2>中等风险，适合稳健用户先模拟观察</h2>
            </div>
            <StatusBadge status="Warning" />
          </div>
          <ul className="safetyList">
            <li>风险等级：中等风险</li>
            <li>最大回撤：-11.8%，最大回撤区间：2024-04 至 2024-06</li>
            <li>波动率：15.8%，适合用户：steady</li>
            <li>风险解释：收益有吸引力，但需要接受阶段性回撤。</li>
          </ul>
        </article>
      </section>

      <section className="grid two">
        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="meta">交易记录</p>
              <h2>Trade Preview</h2>
            </div>
            <StatusBadge status="OK" />
          </div>
          {['买入 小市值组合', '卖出 弱势持仓', '调仓至动量较强标的'].map((row) => (
            <div className="listRow" key={row}><strong>{row}</strong><span>本地模拟记录</span></div>
          ))}
        </article>

        <details className="panel advancedMetricPanel">
          <summary>高级指标</summary>
          <div className="pillRow">
            {advancedMetrics.map((metric) => (
              <span className="softPill" key={metric}>{metric}</span>
            ))}
          </div>
        </details>
      </section>

      <section className="panel warningPanel">
        <div className="panelHeader">
          <div>
            <p className="meta">安全提示</p>
            <h2>当前仅为回测和模拟交易环境，不连接真实券商，不使用真实资金，不提交真实订单。</h2>
          </div>
          <StatusBadge status="Warning" />
        </div>
      </section>
    </ProductionShell>
  );
}
