type PricingPlanCardProps = {
  name: string;
  status: string;
  priceLabel: string;
  targetUser: string;
  quota: string;
  workspace: string;
  support: string;
  features: string[];
  cta: string;
};

const allowedCtas = ['Demo only', 'Contact planned', 'Not payment button'];

export function PricingPlanCard({ name, status, priceLabel, targetUser, quota, workspace, support, features, cta }: PricingPlanCardProps) {
  const safeCta = allowedCtas.includes(cta) ? cta : 'Demo only';

  return (
    <section className="card moduleCard">
      <div className="cardHeader">
        <h2>Plan name: {name}</h2>
        <span className={status === 'demo' ? 'badge badge-ok' : 'badge badge-warning'}>Status: {status}</span>
      </div>
      <p className="moduleMetric">Price label: {priceLabel}</p>
      <div className="miniGrid">
        <div>
          <strong>Target user</strong>
          <span>{targetUser}</span>
        </div>
        <div>
          <strong>Quota concept</strong>
          <span>{quota}</span>
        </div>
        <div>
          <strong>Workspace concept</strong>
          <span>{workspace}</span>
        </div>
        <div>
          <strong>Support level</strong>
          <span>{support}</span>
        </div>
      </div>
      <div className="divider" />
      <p className="meta">Feature list</p>
      <ul className="featureList">
        {features.map((feature) => (
          <li key={feature}>{feature}</li>
        ))}
      </ul>
      <span className="button ghost">CTA: {safeCta}</span>
    </section>
  );
}
