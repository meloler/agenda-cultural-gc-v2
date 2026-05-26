import { getHeroStats, type HomeCollection } from "../lib/collections";

interface HeroProps {
  collections: HomeCollection[];
  source: "supabase" | "mock";
}

export function Hero({ collections, source }: HeroProps) {
  const stats = getHeroStats(collections);

  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="hero__kicker">{source === "supabase" ? "Eventos reales curados" : "Mock V0 · fallback seguro"}</div>
      <h1 id="hero-title">¿Qué plan te apetece?</h1>
      <p>
        Una guía rápida para descubrir planes en Gran Canaria por intención, momento y calidad,
        no por una lista interminable de fechas.
      </p>
      <div className="hero__stats" aria-label="Resumen de la home">
        <span><strong>{stats.collectionCount}</strong> colecciones</span>
        <span><strong>{stats.eventCount}</strong> {source === "supabase" ? "planes reales" : "planes mock"}</span>
      </div>
    </section>
  );
}
