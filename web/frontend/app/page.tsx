import { ProductionShell } from './components/ProductionShell';

export default function HomePage() {
  return (
    <ProductionShell
      title="Dashboard"
      eyebrow="Production Launch"
      description="A polished SaaS-style shell for local product demos and research platform readiness."
      activePath="/dashboard"
    />
  );
}
