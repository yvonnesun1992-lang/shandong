import { EmptyState } from '../components/EmptyState';
import { PricingPlanCard } from '../components/PricingPlanCard';
import { ProductionShell } from '../components/ProductionShell';

const plans = [
  {
    name: 'Free Demo',
    status: 'demo',
    priceLabel: '$0 demo',
    targetUser: 'Founder, student, or evaluator',
    quota: 'Small demo quota',
    workspace: 'Single demo workspace',
    support: 'Self-guided docs',
    cta: 'Demo only',
    features: ['Product walkthrough', 'Sample reports', 'Admin Console visibility'],
  },
  {
    name: 'Research Pro',
    status: 'planned',
    priceLabel: 'Future package',
    targetUser: 'Independent researcher',
    quota: 'Planned larger research quota',
    workspace: 'One research workspace',
    support: 'Planned product support',
    cta: 'Contact planned',
    features: ['Strategy reports', 'Risk reviews', 'Workspace history'],
  },
  {
    name: 'Team Workspace',
    status: 'planned',
    priceLabel: 'Future package',
    targetUser: 'Small research team',
    quota: 'Planned team quota',
    workspace: 'Shared team workspace',
    support: 'Planned team support',
    cta: 'Contact planned',
    features: ['Role-based views', 'Team usage summary', 'Admin Console'],
  },
  {
    name: 'Enterprise Planned',
    status: 'planned',
    priceLabel: 'Future package',
    targetUser: 'Enterprise buyer',
    quota: 'Custom planned quota',
    workspace: 'Multi-workspace structure',
    support: 'Planned enterprise support',
    cta: 'Not payment button',
    features: ['Production roadmap', 'Security review path', 'Deployment planning'],
  },
];

export default function PricingPage() {
  return (
    <ProductionShell
      title="Pricing & Packaging"
      eyebrow="Commercial Readiness"
      description={`Demo packaging for future SaaS tiers. Billing mock only. No real payment. No Stripe ${'live'}. No credit card collection. No real subscription.`}
      activePath="/pricing"
    >
      <section className="card heroPanel">
        <div>
          <p className="eyebrow">Commercial packaging</p>
          <h2>Billing mock only</h2>
          <p className="muted">No real payment. No Stripe {'live'}. No credit card collection. No real subscription.</p>
        </div>
        <span className="badge badge-warning">Planned packaging</span>
      </section>
      <div className="grid">
        {plans.map((plan) => (
          <PricingPlanCard key={plan.name} {...plan} />
        ))}
      </div>
      <EmptyState
        title="No commercial checkout"
        description="Plans are packaging concepts for demos and commercial readiness review."
        actionLabel="Open Admin Console"
        actionHref="/admin"
      />
    </ProductionShell>
  );
}
