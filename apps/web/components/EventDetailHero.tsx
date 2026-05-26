import type { EventCandidate } from "@agenda-cultural-gc/event-intelligence";
import { primaryTag } from "../lib/events/presentation";

export function EventDetailHero({ event, signal }: { event: EventCandidate; signal: string }) {
  return (
    <section className="detail-hero" aria-labelledby="event-title">
      <div className="detail-hero__media">
        {event.image_url ? (
          <img src={event.image_url} alt={`Imagen de ${event.title}`} />
        ) : (
          <div className="detail-hero__placeholder" role="img" aria-label="Evento sin imagen disponible">
            GC
          </div>
        )}
        <span>{signal}</span>
      </div>
      <div className="detail-hero__copy">
        <p>{primaryTag(event)}</p>
        <h1 id="event-title">{event.title}</h1>
      </div>
    </section>
  );
}
