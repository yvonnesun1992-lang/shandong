type PermissionNoticeProps = {
  mode: 'login' | 'denied' | 'expired';
};

const copy = {
  login: ['Demo login recommended', 'Sign in as Admin, User, or Viewer to send role-aware demo requests.'],
  denied: ['Permission denied', 'This role cannot access the requested admin view. Try the Admin demo role.'],
  expired: ['Session expired or unavailable', 'Clear the local demo session and sign in again.'],
};

export function PermissionNotice({ mode }: PermissionNoticeProps) {
  const [title, description] = copy[mode];
  return (
    <section className="permissionNotice">
      <strong>{title}</strong>
      <p>{description}</p>
      <a className="button" href="/login">
        Go to Demo Login
      </a>
    </section>
  );
}
