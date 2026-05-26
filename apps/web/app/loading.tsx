export default function Loading() {
  return (
    <main className="app-shell" aria-live="polite" aria-busy="true">
      <section className="state-card state-card--soft">
        <p>Cargando planes</p>
        <h1>Preparando recomendaciones.</h1>
        <span>Estamos ordenando eventos por intención, fecha y calidad de datos.</span>
      </section>
    </main>
  );
}
