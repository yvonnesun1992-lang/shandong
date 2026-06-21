import { ProductionShell } from '../components/ProductionShell';

const layout = 'card layout';

export default function SettingsPage() {
  return (
    <ProductionShell
      title="Settings"
      eyebrow="Admin"
      description="Review local configuration posture and product shell defaults for demos."
      activePath="/settings"
    />
  );
}
