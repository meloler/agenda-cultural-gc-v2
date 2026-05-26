import { EventRail } from "../components/EventRail";
import { Hero } from "../components/Hero";
import { IntentCloud } from "../components/IntentCloud";
import { buildHomeCollections } from "../lib/collections";

export default function HomePage() {
  const collections = buildHomeCollections();

  return (
    <main className="app-shell" aria-labelledby="page-title">
      <header className="topbar" aria-label="Cabecera principal">
        <div>
          <p>Agenda Cultural GC</p>
          <span>Descubre qué hacer hoy y este finde en Gran Canaria.</span>
        </div>
      </header>

      <Hero collections={collections} />
      <IntentCloud />

      <section className="collections" aria-labelledby="collections-title">
        <div className="section-heading section-heading--wide">
          <p>Estanterías vivas</p>
          <h2 id="collections-title">Planes ordenados por intención</h2>
        </div>
        {collections.length > 0 ? (
          collections.map((collection) => <EventRail collection={collection} key={collection.id} />)
        ) : (
          <p className="empty-state">No hay planes mock publicables para esta demo.</p>
        )}
      </section>
    </main>
  );
}
