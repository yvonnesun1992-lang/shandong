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

export function getApiBaseUrl() {
  return (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
}

export async function apiGet<T>(path: string): Promise<ApiResult<T>> {
  const target = `${getApiBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`;
  try {
    const response = await fetch(target, { cache: 'no-store' });
    const payload = (await response.json().catch(() => ({}))) as ApiEnvelope<T>;
    const cleanPayload = sanitizePayload(payload);
    if (!response.ok || cleanPayload.success === false) {
      return {
        ok: false,
        data: null,
        warning: cleanPayload.warning ?? [],
        errorMessage: sanitizeText(cleanPayload.error?.message ?? 'API request unavailable'),
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
