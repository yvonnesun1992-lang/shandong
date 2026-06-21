import { ProductionShell } from '../components/ProductionShell';

const layout = 'card layout';

export default function RiskPage() {
  return (
    <ProductionShell
      title="Risk"
      eyebrow="Controls"
      description="Review risk posture, stress boundaries, and research-only safeguards without live execution."
      activePath="/risk"
    />
  );
}
