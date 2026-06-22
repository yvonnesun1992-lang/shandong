import { EmptyState } from '../components/EmptyState';
import { FirstRunChecklist } from '../components/FirstRunChecklist';
import { MetricCard } from '../components/MetricCard';
import { ProductionShell } from '../components/ProductionShell';

const safetyBoundaries = [
  'Research mode only',
  'No broker connection',
  'No auto trading',
  'No real payment',
  'No production identity',
  'No external cloud connected',
  'No AI API connected',
  'Demo / local mode',
];

const journey = [
  ['1', 'Open Dashboard', 'Start with system status and research-mode context.'],
  ['2', 'Demo Login', 'Choose Admin, User, or Viewer for local demo UX.'],
  ['3', 'Admin Console', 'Review readiness, identity planning, observability, and deployment dry run.'],
  ['4', 'API Docs', 'Inspect the product API surface for local demos.'],
];

export default function OnboardingPage() {
  return (
    <ProductionShell
      title="Welcome to Shandong"
      eyebrow="Product Onboarding"
      description="AI-era investment research dashboard and quant research SaaS demo for safe product walkthroughs."
      activePath="/onboarding"
    >
      <div className="summaryStrip">
        <MetricCard title="Product mode" value="Demo" description="Local research control plane for product demos." />
        <MetricCard title="Safety" value="Research" description="No broker connection and no auto trading." status="Warning" />
        <MetricCard title="Next step" value="Dashboard" description="Start with the product overview." />
      </div>
      <section className="card">
        <div className="cardHeader">
          <h2>What this product does</h2>
          <span className="badge badge-ok">Demo ready</span>
        </div>
        <p className="muted">
          Shandong helps demo strategy research, report workflows, risk review, platform readiness, and SaaS-style operations in one product shell.
        </p>
      </section>
      <section className="card">
        <div className="cardHeader">
          <h2>What this product does not do</h2>
          <span className="badge badge-warning">Safety boundary</span>
        </div>
        <div className="miniGrid">
          {safetyBoundaries.map((item) => (
            <div key={item}>
              <strong>{item}</strong>
              <span>Visible during first-run demos.</span>
            </div>
          ))}
        </div>
      </section>
      <section className="card">
        <div className="cardHeader">
          <h2>Demo journey</h2>
          <span className="badge badge-ok">5 minutes</span>
        </div>
        <div className="grid">
          {journey.map(([step, title, description]) => (
            <div className="card" key={step}>
              <p className="eyebrow">Step {step}</p>
              <h2>{title}</h2>
              <p className="muted">{description}</p>
            </div>
          ))}
        </div>
      </section>
      <FirstRunChecklist />
      <section className="card heroPanel">
        <div>
          <p className="eyebrow">Next actions</p>
          <h2>Pick the demo path</h2>
          <p className="muted">Start with Dashboard, log in with a demo role, or inspect Admin Console and API Docs.</p>
        </div>
        <div className="buttonRow">
          <a className="button" href="/dashboard">
            Open Dashboard
          </a>
          <a className="button button-secondary" href="/login">
            Demo Login
          </a>
          <a className="button button-secondary" href="/admin">
            Admin Console
          </a>
          <a className="button button-secondary" href="/api-docs">
            API Docs
          </a>
        </div>
      </section>
      <EmptyState
        title="First-run experience is demo-safe"
        description="This onboarding flow explains what the system can show and what it intentionally cannot do."
        actionLabel="Open Dashboard"
        actionHref="/dashboard"
      />
    </ProductionShell>
  );
}
