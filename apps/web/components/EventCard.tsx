import Link from "next/link";
import type { HomeEvent } from "../lib/collections";
import { formatDate, formatTime, placeLabel, priceLabel, primaryTag } from "../lib/events/presentation";

export function EventCard({ item }: { item: HomeEvent }) {
  const { event } = item;
  const time = formatTime(event.starts_at);
  const reason = item.reasons[0]?.replace(/^Suma: /, "") ?? "Encaja con esta colección";

  return (
    <Link className="event-card" href={`/events/${encodeURIComponent(event.id)}`} aria-label={`Abrir ficha de ${event.title}`}>
      <article>
        <div className="event-card__media">
          {event.image_url ? (
            <img src={event.image_url} alt={`Imagen de ${event.title}`} loading="lazy" />
          ) : (
            <div className="event-card__placeholder" role="img" aria-label="Evento sin imagen disponible">
              GC
            </div>
          )}
          <span className="event-card__signal">{item.signal}</span>
        </div>
        <div className="event-card__body">
          <p className="event-card__meta">
            {formatDate(event.starts_at)}{time ? ` · ${time}` : ""}
          </p>
          <h3>{event.title}</h3>
          <p className="event-card__place">{placeLabel(event)}</p>
          <div className="event-card__facts" aria-label="Datos clave del evento">
            <span>{priceLabel(event)}</span>
            <span>{primaryTag(event)}</span>
          </div>
          <p className="event-card__reason">Porque: {reason}</p>
        </div>
      </article>
    </Link>
  );
}
