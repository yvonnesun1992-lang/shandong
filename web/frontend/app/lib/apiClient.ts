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
