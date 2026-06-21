'use client';

import { useEffect, useState } from 'react';

import { getStoredRole, isDemoAuthenticated, logoutDemoUser, type DemoRole } from '../lib/authClient';
import { StatusBadge } from './StatusBadge';

export function AuthStatus() {
  const [role, setRole] = useState<DemoRole | null>(null);
  const [active, setActive] = useState(false);

  useEffect(() => {
    setRole(getStoredRole());
    setActive(isDemoAuthenticated());
  }, []);

  function handleLogout() {
    logoutDemoUser();
    setRole(null);
    setActive(false);
  }

  return (
    <section className="authStatus">
      <div>
        <p className="meta">Demo auth</p>
        <strong>{active ? 'Demo session active' : 'Fallback mode'}</strong>
        <p className="muted">Role: {role ?? 'not logged in'}</p>
      </div>
      <StatusBadge status={active ? 'OK' : 'Warning'} />
      {active ? (
        <button className="button button-secondary" type="button" onClick={handleLogout}>
          Logout
        </button>
      ) : (
        <a className="button" href="/login">
          Demo Login
        </a>
      )}
    </section>
  );
}
