import { ProductionShell } from '../components/ProductionShell';

const layout = 'card layout';

export default function ApiDocsPage() {
  return (
    <ProductionShell
      title="API Docs"
      eyebrow="Developer Platform"
      description="Use the API surface for local demos, health checks, and product architecture review."
      activePath="/api-docs"
    />
  );
}
