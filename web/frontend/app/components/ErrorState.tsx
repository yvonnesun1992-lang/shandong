export function ErrorState({ title = 'Using fallback data', description }: { title?: string; description: string }) {
  return (
    <section className="stateBox stateBox-error">
      <strong>{title}</strong>
      <p>{description}</p>
    </section>
  );
}
