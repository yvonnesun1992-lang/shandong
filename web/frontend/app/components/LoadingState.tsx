export function LoadingState({ label = 'Loading platform status' }: { label?: string }) {
  return (
    <section className="stateBox stateBox-loading">
      <span className="loadingDot" />
      <p>{label}</p>
    </section>
  );
}
