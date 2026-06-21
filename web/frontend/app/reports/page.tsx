import { ProductionShell } from '../components/ProductionShell';

const layout = 'card layout';

export default function ReportsPage() {
  return (
    <ProductionShell
      title="Reports"
      eyebrow="Research Archive"
      description="Browse generated research outputs, archive context, and report readiness in one consistent view."
      activePath="/reports"
    />
  );
}
