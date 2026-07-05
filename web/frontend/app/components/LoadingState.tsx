export function LoadingState({ label = 'Initializing Quant Engine...' }: { label?: string }) {
  return (
    <section className="stateBox stateBox-loading">
      <span className="loadingDot" />
      <div>
        <strong>Shandong Quantitative System</strong>
        <p>{label}</p>
        <span>Paper Trading Mode</span>
      </div>
    </section>
  );
}
