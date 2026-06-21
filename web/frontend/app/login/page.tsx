'use client';

import { useState } from 'react';

import { AuthStatus } from '../components/AuthStatus';
import { ErrorState } from '../components/ErrorState';
import { ProductionShell } from '../components/ProductionShell';
import { loginDemoUser, type DemoRole } from '../lib/authClient';
import { getIdentityBoundaryNotice, getIdentityMode, getIdentityProviderLabel } from '../lib/identityStatus';

const roles: { role: DemoRole; title: string; description: string }[] = [
  { role: 'admin', title: 'Admin', description: 'Full demo access for Admin Console review.' },
  { role: 'user', title: 'User', description: 'Research workflow access with limited admin controls.' },
  { role: 'viewer', title: 'Viewer', description: 'Read-focused role for safe product demonstrations.' },
];

export default function LoginPage() {
  const [selectedRole, setSelectedRole] = useState<DemoRole>('admin');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  async function handleLogin() {
    setError('');
    setMessage('');
    const result = await loginDemoUser(selectedRole);
    if (!result.ok) {
      setError(result.errorMessage ?? 'Demo login failed');
      return;
    }
    setMessage(`Demo ${selectedRole} login ready. Continue to Dashboard or Admin Console.`);
  }

  return (
    <ProductionShell
      title="Demo Login"
      eyebrow="Mock login"
      description="Choose a demo role for local session UX. This is not production identity and does not use real credentials."
      activePath="/settings"
    >
      <AuthStatus />
      {error ? <ErrorState description={error} /> : null}
      {message ? (
        <section className="stateBox stateBox-loading">
          <p>{message}</p>
          <a className="button" href="/dashboard">
            Dashboard
          </a>
          <a className="button button-secondary" href="/admin">
            Admin Console
          </a>
        </section>
      ) : null}
      <section className="card">
        <div className="cardHeader">
          <h2>Identity boundary</h2>
          <span className="badge badge-warning">{getIdentityMode()}</span>
        </div>
        <p className="muted">{getIdentityBoundaryNotice()}</p>
        <div className="miniGrid">
          <div>
            <strong>Demo login only</strong>
            <span>{getIdentityProviderLabel()}</span>
          </div>
          <div>
            <strong>Not production identity</strong>
            <span>Production identity is planned.</span>
          </div>
          <div>
            <strong>No OAuth connected</strong>
            <span>External provider is not connected.</span>
          </div>
          <div>
            <strong>No password stored</strong>
            <span>Demo role selection only.</span>
          </div>
          <div>
            <strong>No external provider connected</strong>
            <span>Provider setup remains planning-only.</span>
          </div>
        </div>
      </section>
      <section className="card">
        <div className="cardHeader">
          <h2>Role selection</h2>
          <span className="badge badge-warning">Research / Demo mode</span>
        </div>
        <p className="muted">No broker connection. No auto trading. This mock login stores a local demo session only.</p>
        <div className="roleGrid">
          {roles.map((item) => (
            <button className={selectedRole === item.role ? 'roleCard selected' : 'roleCard'} key={item.role} type="button" onClick={() => setSelectedRole(item.role)}>
              <strong>{item.title}</strong>
              <span>{item.description}</span>
            </button>
          ))}
        </div>
        <button className="button" type="button" onClick={handleLogin}>
          Continue with {selectedRole}
        </button>
      </section>
    </ProductionShell>
  );
}
