import { EventRail } from "../components/EventRail";
import { Hero } from "../components/Hero";
import { IntentCloud } from "../components/IntentCloud";
import { getHomeEvents } from "../lib/events/get-home-events";

export default async function HomePage() {
  const { collections, source, warning } = await getHomeEvents();

  return (
    <main className="app-shell" aria-labelledby="page-title">
      <header className="topbar" aria-label="Cabecera principal">
        <div>
          <p>Agenda Cultural GC</p>
          <span>Descubre qué hacer hoy y este finde en Gran Canaria.</span>
        </div>
      </header>

      {warning ? (
        <aside className="source-banner" aria-label="Estado de la fuente de datos">
          {warning}
        </aside>
      ) : (
        <aside className="source-banner source-banner--live" aria-label="Estado de la fuente de datos">
          Eventos reales curados desde Supabase.
        </aside>
      )}

      <Hero collections={collections} source={source} />
      <IntentCloud />

      <section className="collections" aria-labelledby="collections-title">
        <div className="section-heading section-heading--wide">
          <p>Estanterías vivas</p>
          <h2 id="collections-title">Planes ordenados por intención</h2>
        </div>
        {collections.length > 0 ? (
          collections.map((collection) => <EventRail collection={collection} key={collection.id} />)
        ) : (
          <p className="empty-state">No hay planes publicables para mostrar ahora mismo.</p>
        )}
      </section>
    </main>
  );
}
