import { ProductionShell } from '../components/ProductionShell';

const layout = 'card layout';

export default function StrategyPage() {
  return (
    <ProductionShell
      title="Strategy Center"
      eyebrow="Research Workflow"
      description="Start research-oriented strategy workflows while keeping the platform in safe demo mode."
      activePath="/strategy"
    />
  );
}
