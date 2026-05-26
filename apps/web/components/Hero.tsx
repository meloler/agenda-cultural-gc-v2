import { getHeroStats, type HomeCollection } from "../lib/collections";

interface HeroProps {
  collections: HomeCollection[];
}

export function Hero({ collections }: HeroProps) {
  const stats = getHeroStats(collections);

  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="hero__kicker">Mock V0 · sin conexión a producción</div>
      <h1 id="hero-title">¿Qué plan te apetece?</h1>
      <p>
        Una guía rápida para descubrir planes en Gran Canaria por intención, momento y calidad,
        no por una lista interminable de fechas.
      </p>
      <div className="hero__stats" aria-label="Resumen de la demo">
        <span><strong>{stats.collectionCount}</strong> colecciones</span>
        <span><strong>{stats.eventCount}</strong> planes mock</span>
      </div>
    </section>
  );
}
