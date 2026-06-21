type PageHeaderProps = {
  eyebrow: string;
  title: string;
  description: string;
  actionLabel?: string;
  actionHref?: string;
};

export function PageHeader({ eyebrow, title, description, actionLabel, actionHref }: PageHeaderProps) {
  return (
    <header className="pageHeader">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="pageDescription">{description}</p>
      </div>
      {actionLabel && actionHref ? (
        <a className="button" href={actionHref}>
          {actionLabel}
        </a>
      ) : null}
    </header>
  );
}
