import Link from "next/link";

export default function EventNotFound() {
  return (
    <main className="detail-shell detail-shell--state">
      <Link className="back-link" href="/">← Volver a la home</Link>
      <section className="state-card">
        <p>Evento no encontrado</p>
        <h1>No encontramos esta ficha.</h1>
        <span>Puede que el evento ya no esté disponible o no tenga datos publicables.</span>
      </section>
    </main>
  );
}
