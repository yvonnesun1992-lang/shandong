import { getStoredSession } from './authClient';
import { sanitizePayload, sanitizeText } from './sanitize';

export type ApiResult<T> = {
  ok: boolean;
  data: T | null;
  warning: string[];
  errorMessage?: string;
};

type ApiEnvelope<T> = {
  success?: boolean;
  data?: T;
  warning?: string[];
  error?: {
    message?: string;
  };
};

type ApiGetOptions = {
  sessionId?: string | null;
};

export function getApiBaseUrl() {
  return (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
}

function friendlyAuthError(status: number) {
  if (status === 401) return 'Authentication required';
  if (status === 403) return 'Permission denied';
  return 'Session expired or unavailable';
}

export async function apiGet<T>(path: string, options: ApiGetOptions = {}): Promise<ApiResult<T>> {
  const target = `${getApiBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`;
  const sessionValue = options.sessionId ?? getStoredSession();
  const headers: Record<string, string> = sessionValue ? { 'X-Session-ID': sessionValue } : {};
  try {
    const response = await fetch(target, { cache: 'no-store', headers });
    const payload = (await response.json().catch(() => ({}))) as ApiEnvelope<T>;
    const cleanPayload = sanitizePayload(payload);
    if (!response.ok || cleanPayload.success === false) {
      return {
        ok: false,
        data: null,
        warning: cleanPayload.warning ?? [],
        errorMessage: sanitizeText(response.status === 401 || response.status === 403 ? friendlyAuthError(response.status) : cleanPayload.error?.message ?? 'API request unavailable'),
      };
    }
    return {
      ok: true,
      data: sanitizePayload(cleanPayload.data ?? null) as T,
      warning: cleanPayload.warning ?? [],
    };
  } catch {
    return {
      ok: false,
      data: null,
      warning: ['Using safe fallback data'],
      errorMessage: 'Backend API is unavailable',
    };
  }
}

export function fetchAdminConsole() {
  return apiGet<Record<string, unknown>>('/api/v2/admin/console');
}

export function fetchReadiness() {
  return apiGet<Record<string, unknown>>('/api/v2/system/readiness');
}

export function fetchLiveness() {
  return apiGet<Record<string, unknown>>('/api/v2/system/liveness');
}

export function fetchSecurityHealth() {
  return apiGet<Record<string, unknown>>('/api/v2/system/security-health');
}

export function fetchWorkspaceHealth() {
  return apiGet<Record<string, unknown>>('/api/v2/system/workspace-health');
}

export function fetchBillingHealth() {
  return apiGet<Record<string, unknown>>('/api/v2/system/billing-health');
}

export function fetchObservability() {
  return apiGet<Record<string, unknown>>('/api/v2/system/observability');
}

export function fetchDeploymentDryRun() {
  return apiGet<Record<string, unknown>>('/api/v2/system/deployment-dry-run');
}

export function fetchV3ReleaseCandidate() {
  return apiGet<Record<string, unknown>>('/api/v2/system/v3-release-candidate');
}

export function fetchOnboarding() {
  return apiGet<Record<string, unknown>>('/api/v2/system/onboarding');
}

export function fetchWorkspaceDemo() {
  return apiGet<Record<string, unknown>>('/api/v2/system/workspace-demo');
}

export function fetchPricingPlan() {
  return apiGet<Record<string, unknown>>('/api/v2/system/pricing-plan');
}

export function fetchProductionReadiness() {
  return apiGet<Record<string, unknown>>('/api/v2/system/production-readiness');
}

export function fetchProductionDatabase() {
  return apiGet<Record<string, unknown>>('/api/v2/system/production-database');
}

export function fetchIdentityIntegration() {
  return apiGet<Record<string, unknown>>('/api/v2/system/identity-integration');
}

export function fetchDeploymentTarget() {
  return apiGet<Record<string, unknown>>('/api/v2/system/deployment-target');
}

export function fetchV5MonitoringSummary() {
  return apiGet<Record<string, unknown>>('/api/v5/monitoring/summary');
}

export function fetchV5MonitoringPnl() {
  return apiGet<Record<string, unknown>>('/api/v5/monitoring/pnl');
}

export function fetchV5MonitoringPositions() {
  return apiGet<Record<string, unknown>>('/api/v5/monitoring/positions');
}

export function fetchV5MonitoringSignals() {
  return apiGet<Record<string, unknown>>('/api/v5/monitoring/signals');
}

export function fetchV5MonitoringTrades() {
  return apiGet<Record<string, unknown>>('/api/v5/monitoring/trades');
}

export function fetchV5MonitoringErrors() {
  return apiGet<Record<string, unknown>>('/api/v5/monitoring/errors');
}

export function fetchV5MonitoringHealth() {
  return apiGet<Record<string, unknown>>('/api/v5/monitoring/health');
}

export function fetchV5MonitoringRisk() {
  return apiGet<Record<string, unknown>>('/api/v5/monitoring/risk');
}

export function fetchV5MonitoringSoakReport() {
  return apiGet<Record<string, unknown>>('/api/v5/monitoring/soak-report');
}

export function fetchV5DeploymentDryRun() {
  return apiGet<Record<string, unknown>>('/api/v5/deployment/dry-run');
}

export function fetchV5DeploymentReadiness() {
  return apiGet<Record<string, unknown>>('/api/v5/deployment/readiness');
}

export function fetchV5LivePaperStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/live-paper/status');
}

export function fetchV5LivePaperConfig() {
  return apiGet<Record<string, unknown>>('/api/v5/live-paper/config');
}

export function fetchV5LivePaperLatestTick() {
  return apiGet<Record<string, unknown>>('/api/v5/live-paper/latest-tick');
}

export function fetchV5LivePaperSummary() {
  return apiGet<Record<string, unknown>>('/api/v5/live-paper/summary');
}

export function fetchV5LiveAlphaStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/live-alpha/status');
}

export function fetchV5LiveAlphaLatestSignals() {
  return apiGet<Record<string, unknown>>('/api/v5/live-alpha/latest-signals');
}

export function fetchV5LiveAlphaSummary() {
  return apiGet<Record<string, unknown>>('/api/v5/live-alpha/summary');
}

export function fetchV5LiveAlphaBufferStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/live-alpha/buffer-status');
}

export function fetchV5BrokerStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/broker/status');
}

export function fetchV5BrokerReadiness() {
  return apiGet<Record<string, unknown>>('/api/v5/broker/readiness');
}

export function fetchV5BrokerSafety() {
  return apiGet<Record<string, unknown>>('/api/v5/broker/safety');
}

export function fetchV5BrokerOrderMapping() {
  return apiGet<Record<string, unknown>>('/api/v5/broker/order-mapping');
}

export function fetchV5ApprovalStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/approval/status');
}

export function fetchV5ApprovalReadiness() {
  return apiGet<Record<string, unknown>>('/api/v5/approval/readiness');
}

export function fetchV5ApprovalPolicy() {
  return apiGet<Record<string, unknown>>('/api/v5/approval/policy');
}

export function fetchV5ApprovalAuditSummary() {
  return apiGet<Record<string, unknown>>('/api/v5/approval/audit-summary');
}

export function fetchV5SandboxStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox/status');
}

export function fetchV5SandboxProviderPlan() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox/provider-plan');
}

export function fetchV5SandboxCredentialPolicy() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox/credential-policy');
}

export function fetchV5SandboxOrderLifecycle() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox/order-lifecycle');
}

export function fetchV5SandboxSafetyChecklist() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox/safety-checklist');
}

export function fetchV5SandboxRollbackPlan() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox/rollback-plan');
}

export function fetchV5SandboxSimStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-sim/status');
}

export function fetchV5SandboxSimAccount() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-sim/account');
}

export function fetchV5SandboxSimOrders() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-sim/orders');
}

export function fetchV5SandboxSimFills() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-sim/fills');
}

export function fetchV5SandboxSimScenarios() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-sim/scenarios');
}

export function fetchV5SandboxSimSummary() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-sim/summary');
}
