import { ProductionShell } from '../components/ProductionShell';

const layout = 'card layout';

export default function LoginPage() {
  return (
    <ProductionShell
      title="Login"
      eyebrow="Access"
      description="Mock login shell for local demos. Production identity remains a planned future layer."
      activePath="/settings"
    />
  );
}
