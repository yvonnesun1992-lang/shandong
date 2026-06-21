type EmptyStateProps = {
  title: string;
  description: string;
  actionLabel?: string;
  actionHref?: string;
};

export function EmptyState({ title, description, actionLabel, actionHref }: EmptyStateProps) {
  return (
    <section className="emptyState">
      <h2>{title}</h2>
      <p>{description}</p>
      {actionLabel && actionHref ? (
        <a className="button" href={actionHref}>
          {actionLabel}
        </a>
      ) : null}
    </section>
  );
}
