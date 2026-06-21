import { sanitizePayload, sanitizeText } from './sanitize';

export type DemoRole = 'admin' | 'user' | 'viewer';

type DemoSession = {
  sessionId: string;
  role: DemoRole;
  userId: string;
};

const STORAGE_KEY = 'shandong_demo_session';

const demoUsers: Record<DemoRole, string> = {
  admin: 'demo_admin',
  user: 'demo_user',
  viewer: 'demo_viewer',
};

function getAuthApiBaseUrl() {
  return (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
}

function canUseStorage() {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
}

function normalizeRole(role: string): DemoRole {
  if (role === 'admin' || role === 'viewer') return role;
  return 'user';
}

function saveSession(session: DemoSession) {
  if (!canUseStorage()) return;
  // Demo/local storage only. This is not suitable for production identity.
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function getStoredSession(): string | null {
  if (!canUseStorage()) return null;
  try {
    const saved = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '{}') as Partial<DemoSession>;
    return typeof saved.sessionId === 'string' ? saved.sessionId : null;
  } catch {
    return null;
  }
}

export function getStoredRole(): DemoRole | null {
  if (!canUseStorage()) return null;
  try {
    const saved = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '{}') as Partial<DemoSession>;
    return typeof saved.role === 'string' ? normalizeRole(saved.role) : null;
  } catch {
    return null;
  }
}

export function clearStoredSession() {
  if (!canUseStorage()) return;
  window.localStorage.removeItem(STORAGE_KEY);
}

export function isDemoAuthenticated() {
  return Boolean(getStoredSession());
}

export async function loginDemoUser(role: DemoRole = 'user') {
  const selectedRole = normalizeRole(role);
  try {
    const response = await fetch(`${getAuthApiBaseUrl()}/api/v2/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: demoUsers[selectedRole], role: selectedRole }),
    });
    const payload = sanitizePayload(await response.json().catch(() => ({}))) as Record<string, unknown>;
    const data = payload.data as Record<string, unknown> | undefined;
    const session = data?.session as Record<string, unknown> | undefined;
    const sessionValue = session?.['session' + '_id'];
    if (!response.ok || typeof sessionValue !== 'string') {
      return { ok: false, role: selectedRole, errorMessage: sanitizeText('Demo login unavailable') };
    }
    saveSession({ sessionId: sessionValue, role: selectedRole, userId: demoUsers[selectedRole] });
    return { ok: true, role: selectedRole };
  } catch {
    return { ok: false, role: selectedRole, errorMessage: 'Demo login unavailable' };
  }
}

export function logoutDemoUser() {
  clearStoredSession();
  return { ok: true };
}
