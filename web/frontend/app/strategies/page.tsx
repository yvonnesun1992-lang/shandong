import { ProductionShell } from '../components/ProductionShell';
import { StatusBadge } from '../components/StatusBadge';

const categories = ['新手推荐', '稳健收益', '小市值策略', '红利低波策略', '低估值策略', '动量趋势策略', '行业轮动策略', '指数增强策略'];

const strategies = [
  {
    id: 'small_cap_momentum',
    name: '小市值动量策略',
    category: '小市值策略',
    risk: '中',
    market: '震荡偏多',
    description: '寻找近期表现较强的小市值股票，用模拟组合观察趋势延续。',
    fit: '适合能接受波动、想体验进阶策略的用户。',
  },
  {
    id: 'dividend_low_vol',
    name: '红利低波策略',
    category: '红利低波策略',
    risk: '低',
    market: '震荡',
    description: '偏向高分红、低波动资产，适合更稳健的观察方式。',
    fit: '适合第一次使用量化系统、重视回撤控制的用户。',
  },
  {
    id: 'csi300_enhanced',
    name: '沪深300增强策略',
    category: '指数增强策略',
    risk: '低',
    market: '趋势向上',
    description: '以宽基指数为基准，用温和增强方式观察超额收益。',
    fit: '适合想先从指数投资体验开始的用户。',
  },
  {
    id: 'bank_rotation',
    name: '银行股轮动策略',
    category: '稳健收益',
    risk: '低',
    market: '防御市场',
    description: '在银行板块内部做稳健轮动，关注低波动和防御属性。',
    fit: '适合偏保守、希望先看稳定模拟曲线的用户。',
  },
];

const filters = ['风险等级：低 / 中 / 高', '适合市场：牛 / 熊 / 震荡', '策略类型：动量 / 红利 / 低估值 / 指数增强', '适合人群：新手 / 稳健 / 进阶'];

export default function StrategiesPage() {
  return (
    <ProductionShell
      title="策略中心"
      eyebrow="User Friendly Strategy Library"
      description="找到适合你的量化投资策略，不需要写代码。"
      activePath="/strategies"
      actionLabel="一键回测推荐策略"
      actionHref="/strategies/small_cap_momentum"
    >
      <section className="panel strategySearchPanel">
        <div className="panelHeader">
          <div>
            <p className="meta">策略搜索</p>
            <h2>搜索策略：小市值、红利、动量、低估值、指数增强</h2>
          </div>
          <StatusBadge status="OK" />
        </div>
        <input className="searchInput" aria-label="搜索策略" placeholder="搜索策略：小市值、红利、动量、低估值、指数增强" />
        <div className="filterGrid">
          {filters.map((filter) => (
            <button className="filterPill" type="button" key={filter}>
              {filter}
            </button>
          ))}
        </div>
      </section>

      <section className="grid two">
        <article className="panel recommendationPanel">
          <div className="panelHeader">
            <div>
              <p className="meta">系统推荐</p>
              <h2>小市值动量策略</h2>
            </div>
            <StatusBadge status="Warning" />
          </div>
          <p className="muted">适合震荡偏多市场，风险等级中。建议先运行回测，再加入模拟交易观察。</p>
          <div className="ctaRow">
            <a className="button" href="/strategies/small_cap_momentum">一键回测</a>
            <a className="button button-secondary" href="/strategies/small_cap_momentum">加入模拟交易</a>
          </div>
        </article>

        <article className="panel">
          <div className="panelHeader">
            <div>
              <p className="meta">新手推荐</p>
              <h2>先从低波动和指数增强开始</h2>
            </div>
            <StatusBadge status="OK" />
          </div>
          <p className="muted">普通用户不需要看代码，先理解收益、回撤、胜率和适合市场即可。</p>
          <div className="pillRow">
            {categories.slice(0, 5).map((category) => (
              <span className="softPill" key={category}>{category}</span>
            ))}
          </div>
        </article>
      </section>

      <section className="strategyCardGrid">
        {strategies.map((strategy) => (
          <article className="strategyCard" key={strategy.id}>
            <div className="cardHeader">
              <div>
                <p className="meta">{strategy.category}</p>
                <h2>{strategy.name}</h2>
              </div>
              <span className="badge badge-warning">风险 {strategy.risk}</span>
            </div>
            <p className="muted">{strategy.description}</p>
            <div className="strategyFacts">
              <span>适合市场：{strategy.market}</span>
              <span>{strategy.fit}</span>
            </div>
            <div className="ctaRow">
              <a className="button" href={`/strategies/${strategy.id}`}>一键回测</a>
              <a className="button button-secondary" href={`/strategies/${strategy.id}`}>加入模拟交易</a>
            </div>
          </article>
        ))}
      </section>

      <section className="panel warningPanel">
        <div className="panelHeader">
          <div>
            <p className="meta">安全边界</p>
            <h2>当前仅支持回测和模拟交易</h2>
          </div>
          <StatusBadge status="Warning" />
        </div>
        <p className="muted">不连接券商，不读取账户，不提交订单，不接真实资金。策略中心只负责帮助普通用户选择和理解策略。</p>
      </section>
    </ProductionShell>
  );
}
