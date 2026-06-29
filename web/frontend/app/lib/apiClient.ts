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

export function fetchV5SandboxRobustnessStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-robustness/status');
}

export function fetchV5SandboxRobustnessScenarioMatrix() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-robustness/scenario-matrix');
}

export function fetchV5SandboxRobustnessMultiSymbol() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-robustness/multi-symbol');
}

export function fetchV5SandboxRobustnessFaultCombinations() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-robustness/fault-combinations');
}

export function fetchV5SandboxRobustnessLongRun() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-robustness/long-run');
}

export function fetchV5SandboxRobustnessSummary() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-robustness/summary');
}

export function fetchV5SandboxConnectorStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector/status');
}

export function fetchV5SandboxConnectorInterfaceContract() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector/interface-contract');
}

export function fetchV5SandboxConnectorRequestSchema() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector/request-schema');
}

export function fetchV5SandboxConnectorResponseSchema() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector/response-schema');
}

export function fetchV5SandboxConnectorErrorCodes() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector/error-codes');
}

export function fetchV5SandboxConnectorIdempotency() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector/idempotency');
}

export function fetchV5SandboxConnectorRateLimit() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector/rate-limit');
}

export function fetchV5SandboxConnectorRetryPolicy() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector/retry-policy');
}

export function fetchV5SandboxConnectorCredentialBoundary() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector/credential-boundary');
}

export function fetchV5SandboxConnectorReadiness() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector/readiness');
}

export function fetchV5SandboxConnectorMockStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector-mock/status');
}

export function fetchV5SandboxConnectorMockAccount() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector-mock/account');
}

export function fetchV5SandboxConnectorMockPositions() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector-mock/positions');
}

export function fetchV5SandboxConnectorMockRecentOrders() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector-mock/recent-orders');
}

export function fetchV5SandboxConnectorMockScenarios() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector-mock/scenarios');
}

export function fetchV5SandboxConnectorMockSafety() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector-mock/safety');
}

export function fetchV5SandboxConnectorMockSummary() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-connector-mock/summary');
}

export function fetchV5BrokerAdapterList() {
  return apiGet<Record<string, unknown>>('/api/v5/broker-adapter/list');
}

export function fetchV5BrokerAdapterCapabilities() {
  return apiGet<Record<string, unknown>>('/api/v5/broker-adapter/capabilities');
}

export function fetchV5BrokerAdapterRegistry() {
  return apiGet<Record<string, unknown>>('/api/v5/broker-adapter/registry');
}

export function fetchV5BrokerAdapterFactory() {
  return apiGet<Record<string, unknown>>('/api/v5/broker-adapter/factory');
}

export function fetchV5BrokerAdapterSafety() {
  return apiGet<Record<string, unknown>>('/api/v5/broker-adapter/safety');
}

export function fetchV5SandboxBridgeStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-bridge/status');
}

export function fetchV5SandboxBridgeSession() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-bridge/session');
}

export function fetchV5SandboxBridgeRouting() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-bridge/routing');
}

export function fetchV5SandboxBridgeTransform() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-bridge/transform');
}

export function fetchV5SandboxBridgeNormalize() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-bridge/normalize');
}

export function fetchV5SandboxBridgeRetry() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-bridge/retry');
}

export function fetchV5SandboxBridgeIdempotency() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-bridge/idempotency');
}

export function fetchV5SandboxBridgeSafety() {
  return apiGet<Record<string, unknown>>('/api/v5/sandbox-bridge/safety');
}

export function fetchV5IntegrationStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/integration-test/status');
}

export function fetchV5IntegrationScenarios() {
  return apiGet<Record<string, unknown>>('/api/v5/integration-test/scenarios');
}

export function fetchV5IntegrationRun() {
  return apiGet<Record<string, unknown>>('/api/v5/integration-test/run');
}

export function fetchV5IntegrationLayers() {
  return apiGet<Record<string, unknown>>('/api/v5/integration-test/layers');
}

export function fetchV5IntegrationSummary() {
  return apiGet<Record<string, unknown>>('/api/v5/integration-test/summary');
}

export function fetchV5TransitionStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/transition/status');
}

export function fetchV5TransitionReadiness() {
  return apiGet<Record<string, unknown>>('/api/v5/transition/readiness');
}

export function fetchV5TransitionCredentialVault() {
  return apiGet<Record<string, unknown>>('/api/v5/transition/credential-vault');
}

export function fetchV5TransitionEnvironments() {
  return apiGet<Record<string, unknown>>('/api/v5/transition/environments');
}

export function fetchV5TransitionFeatureFlags() {
  return apiGet<Record<string, unknown>>('/api/v5/transition/feature-flags');
}

export function fetchV5TransitionSandboxChecklist() {
  return apiGet<Record<string, unknown>>('/api/v5/transition/sandbox-checklist');
}

export function fetchV5TransitionRealOrderBlocker() {
  return apiGet<Record<string, unknown>>('/api/v5/transition/real-order-blocker');
}

export function fetchV5TransitionKillSwitch() {
  return apiGet<Record<string, unknown>>('/api/v5/transition/kill-switch');
}

export function fetchV5TransitionRollback() {
  return apiGet<Record<string, unknown>>('/api/v5/transition/rollback');
}

export function fetchV5TransitionSafety() {
  return apiGet<Record<string, unknown>>('/api/v5/transition/safety');
}

export function fetchV5ProviderSelectionStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-selection/status');
}

export function fetchV5ProviderSelectionUniverse() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-selection/universe');
}

export function fetchV5ProviderSelectionCapabilityMatrix() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-selection/capability-matrix');
}

export function fetchV5ProviderSelectionRiskMatrix() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-selection/risk-matrix');
}

export function fetchV5ProviderSelectionAccountChecklist() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-selection/account-checklist');
}

export function fetchV5ProviderSelectionApiPermissions() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-selection/api-permissions');
}

export function fetchV5ProviderSelectionMarketData() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-selection/market-data');
}

export function fetchV5ProviderSelectionCompliance() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-selection/compliance');
}

export function fetchV5ProviderSelectionRanking() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-selection/ranking');
}

export function fetchV5ProviderSelectionSafety() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-selection/safety');
}

export function fetchV5ProviderOnboardingStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-onboarding/status');
}

export function fetchV5ProviderOnboardingSelectedProvider() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-onboarding/selected-provider');
}

export function fetchV5ProviderOnboardingAccountOpening() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-onboarding/account-opening');
}

export function fetchV5ProviderOnboardingSandboxAccess() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-onboarding/sandbox-access');
}

export function fetchV5ProviderOnboardingApiKey() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-onboarding/api-key');
}

export function fetchV5ProviderOnboardingMarketData() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-onboarding/market-data');
}

export function fetchV5ProviderOnboardingApprovalRisk() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-onboarding/approval-risk');
}

export function fetchV5ProviderOnboardingSandboxDryRun() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-onboarding/sandbox-dry-run');
}

export function fetchV5ProviderOnboardingSafety() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-onboarding/safety');
}

export function fetchV5ProviderConnectorDesignStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-connector-design/status');
}

export function fetchV5ProviderConnectorDesignFieldMapping() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-connector-design/field-mapping');
}

export function fetchV5ProviderConnectorDesignOrderRequest() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-connector-design/order-request');
}

export function fetchV5ProviderConnectorDesignOrderResponse() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-connector-design/order-response');
}

export function fetchV5ProviderConnectorDesignAccountPosition() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-connector-design/account-position');
}

export function fetchV5ProviderConnectorDesignErrorMapping() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-connector-design/error-mapping');
}

export function fetchV5ProviderConnectorDesignRateLimit() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-connector-design/rate-limit');
}

export function fetchV5ProviderConnectorDesignIdempotency() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-connector-design/idempotency');
}

export function fetchV5ProviderConnectorDesignStateMachine() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-connector-design/state-machine');
}

export function fetchV5ProviderConnectorDesignSafety() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-connector-design/safety');
}

export function fetchV5ProviderMockContractStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-mock-contract/status');
}

export function fetchV5ProviderMockContractPayloads() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-mock-contract/payloads');
}

export function fetchV5ProviderMockContractSchemaValidation() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-mock-contract/schema-validation');
}

export function fetchV5ProviderMockContractRequestMapping() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-mock-contract/request-mapping');
}

export function fetchV5ProviderMockContractResponseNormalization() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-mock-contract/response-normalization');
}

export function fetchV5ProviderMockContractErrorMapping() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-mock-contract/error-mapping');
}

export function fetchV5ProviderMockContractIdempotency() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-mock-contract/idempotency');
}

export function fetchV5ProviderMockContractStateMachine() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-mock-contract/state-machine');
}

export function fetchV5ProviderMockContractSafety() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-mock-contract/safety');
}

export function fetchV5ProviderMockContractSummary() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-mock-contract/summary');
}

export function fetchV5ProviderOfflineReplayStatus() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-offline-replay/status');
}

export function fetchV5ProviderOfflineReplayCatalog() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-offline-replay/catalog');
}

export function fetchV5ProviderOfflineReplayLoad() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-offline-replay/load');
}

export function fetchV5ProviderOfflineReplayRun() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-offline-replay/run');
}

export function fetchV5ProviderOfflineReplayConsistency() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-offline-replay/consistency');
}

export function fetchV5ProviderOfflineReplayRecovery() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-offline-replay/recovery');
}

export function fetchV5ProviderOfflineReplayAudit() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-offline-replay/audit');
}

export function fetchV5ProviderOfflineReplaySafety() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-offline-replay/safety');
}

export function fetchV5ProviderOfflineReplaySummary() {
  return apiGet<Record<string, unknown>>('/api/v5/provider-offline-replay/summary');
}
