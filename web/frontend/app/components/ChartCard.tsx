export function ChartCard() {
  const bars = [62, 80, 48, 72, 90, 66];
  return (
    <section className="card">
      <h2>Usage Trend</h2>
      <div className="chart" aria-label="Usage trend chart">
        {bars.map((height, index) => (
          <div className="bar" key={index} style={{ height: `${height}%` }} />
        ))}
      </div>
    </section>
  );
}
