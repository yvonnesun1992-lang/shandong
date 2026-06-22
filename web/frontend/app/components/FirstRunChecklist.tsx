const checklistItems = [
  'Backend health ready',
  'Frontend shell ready',
  'Demo login available',
  'Admin Console available',
  'Observability local only',
  'Deployment dry run only',
  'V3 release candidate ready',
  'Safety boundaries visible',
];

export function FirstRunChecklist() {
  return (
    <section className="card">
      <div className="cardHeader">
        <h2>First-run checklist</h2>
        <span className="badge badge-ok">Ready</span>
      </div>
      <div className="miniGrid">
        {checklistItems.map((item) => (
          <div key={item}>
            <strong>{item}</strong>
            <span>Demo-safe and local-only.</span>
          </div>
        ))}
      </div>
    </section>
  );
}
