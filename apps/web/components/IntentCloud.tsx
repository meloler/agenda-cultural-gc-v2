import { intentChips } from "../lib/collections";

export function IntentCloud() {
  return (
    <section className="intent" aria-labelledby="intent-title">
      <div className="section-heading">
        <p>Elige una vibra</p>
        <h2 id="intent-title">Nube de intención</h2>
      </div>
      <div className="intent__chips" role="list" aria-label="Intenciones de búsqueda">
        {intentChips.map((chip) => (
          <button className="intent-chip" key={chip} type="button">
            {chip}
          </button>
        ))}
      </div>
    </section>
  );
}
