import type { EventCandidate } from "@agenda-cultural-gc/event-intelligence";
import type { HomeEvent } from "../lib/collections";

function formatDate(value: EventCandidate["starts_at"]): string {
  if (!value) return "Fecha por confirmar";
  return new Intl.DateTimeFormat("es-ES", {
    weekday: "short",
    day: "numeric",
    month: "short",
  }).format(new Date(value));
}

function formatTime(value: EventCandidate["starts_at"]): string | null {
  if (!value || !/T\d{2}:\d{2}/.test(value)) return null;
  return new Intl.DateTimeFormat("es-ES", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function priceLabel(event: EventCandidate): string {
  if (event.is_free) return "Gratis";
  if (typeof event.price === "number") return `${event.price} €`;
  return "Precio por confirmar";
}

function placeLabel(event: EventCandidate): string {
  return event.municipality || event.venue_name || "Lugar por confirmar";
}

function primaryTag(event: EventCandidate): string {
  return event.category || event.tags?.[0] || "Plan";
}

export function EventCard({ item }: { item: HomeEvent }) {
  const { event } = item;
  const time = formatTime(event.starts_at);
  const reason = item.reasons[0]?.replace(/^Suma: /, "") ?? "Encaja con esta colección";

  return (
    <article className="event-card">
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
  );
}
