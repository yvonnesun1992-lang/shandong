import { StatusBadge, type StatusTone } from './StatusBadge';

type MetricCardProps = {
  title: string;
  value: string;
  description: string;
  status?: StatusTone;
  meta?: string;
};

export function MetricCard({ title, value, description, status = 'OK', meta }: MetricCardProps) {
  return (
    <section className="card metricCard">
      <div className="cardHeader">
        <h2>{title}</h2>
        <StatusBadge status={status} />
      </div>
      <p className="metric">{value}</p>
      <p className="muted">{description}</p>
      {meta ? <p className="meta">{meta}</p> : null}
    </section>
  );
}
