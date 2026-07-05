import { ProductionShell } from '../../components/ProductionShell';
import { StatusBadge } from '../../components/StatusBadge';

const strategyNames: Record<string, string> = {
  small_cap_momentum: '小市值动量策略',
  dividend_low_vol: '红利低波策略',
  csi300_enhanced: '沪深300增强策略',
  bank_rotation: '银行股轮动策略',
};

type StrategyDetailPageProps = {
  params: {
    strategyId: string;
  };
};

export default function StrategyDetailPage({ params }: StrategyDetailPageProps) {
  const name = strategyNames[params.strategyId] ?? '量化策略';
  return (
    <ProductionShell
      title={name}
      eyebrow="Strategy Detail"
      description="用普通投资者能理解的方式查看策略定位、风险、回测表现和模拟交易预览。"
      activePath="/strategies"
      actionLabel="一键回测"
      actionHref={`/backtest/${params.strategyId}`}
    >
      <section className="detailLayout">
        <article className="panel sectionStack">
          <div className="panelHeader">
            <div>
              <p className="meta">策略介绍</p>
              <h2>这是什么策略</h2>
            </div>
            <StatusBadge status="OK" />
          </div>
          <p className="muted">该策略用于本地研究、回测和模拟交易展示，帮助用户理解策略在不同市场环境下的表现。</p>

          <div className="infoGrid">
            <div>
              <strong>适合谁</strong>
              <span>希望用简单入口体验量化策略、能先接受模拟结果验证的用户。</span>
            </div>
            <div>
              <strong>不适合谁</strong>
              <span>希望直接实盘下单、读取真实账户或追求确定收益的用户。</span>
            </div>
          </div>
        </article>

        <aside className="panel sectionStack">
          <div className="panelHeader">
            <div>
              <p className="meta">操作入口</p>
              <h2>先验证，再模拟</h2>
            </div>
            <StatusBadge status="Warning" />
          </div>
          <a className="button" href={`/backtest/${params.strategyId}`}>一键回测</a>
          <a className="button button-secondary" href="#paper-preview">加入模拟交易</a>
          <p className="meta">不会连接券商，不会读取账户，不会提交订单。</p>
        </aside>
      </section>

      <section className="grid two">
        <article className="panel" id="backtest">
          <div className="panelHeader">
            <div>
              <p className="meta">回测表现</p>
              <h2>历史样本预览</h2>
            </div>
            <StatusBadge status="OK" />
          </div>
          <div className="miniGrid">
            <div><strong>年化收益</strong><span>12.8%</span></div>
            <div><strong>最大回撤</strong><span>-8.4%</span></div>
            <div><strong>胜率</strong><span>56%</span></div>
            <div><strong>夏普</strong><span>1.18</span></div>
            <div><strong>样本</strong><span>本地演示</span></div>
          </div>
        </article>

        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="meta">风险指标</p>
              <h2>先看风险，再看收益</h2>
            </div>
            <StatusBadge status="Warning" />
          </div>
          <ul className="safetyList">
            <li>单策略波动可能高于稳健组合。</li>
            <li>回测不代表未来收益。</li>
            <li>模拟交易只用于观察，不代表真实成交。</li>
          </ul>
        </article>
      </section>

      <section className="grid two">
        <article className="panel" id="paper-preview">
          <div className="panelHeader">
            <div>
              <p className="meta">模拟交易预览</p>
              <h2>Paper Trading Preview</h2>
            </div>
            <StatusBadge status="OK" />
          </div>
          <p className="muted">系统会用本地模拟账户展示仓位变化、收益曲线和风险提示，但不会产生真实交易。</p>
        </article>

        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="meta">高级代码</p>
              <h2>默认折叠</h2>
            </div>
            <StatusBadge status="Warning" />
          </div>
          <p className="muted">普通用户无需查看代码。高级逻辑保留给研究人员，并默认收起。</p>
        </article>
      </section>
    </ProductionShell>
  );
}
