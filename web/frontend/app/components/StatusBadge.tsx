export type StatusTone = 'OK' | 'Warning' | 'Error';

export function StatusBadge({ status }: { status: StatusTone }) {
  return <span className={`badge badge-${status.toLowerCase()}`}>{status}</span>;
}
