import type { EventCandidate } from "@agenda-cultural-gc/event-intelligence";

export function formatDate(value: EventCandidate["starts_at"]): string {
  if (!value) return "Fecha por confirmar";
  return new Intl.DateTimeFormat("es-ES", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(new Date(value));
}

export function formatTime(value: EventCandidate["starts_at"]): string | null {
  if (!value || !/T\d{2}:\d{2}/.test(value)) return null;
  return new Intl.DateTimeFormat("es-ES", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function priceLabel(event: EventCandidate): string {
  if (event.is_free) return "Gratis";
  if (typeof event.price === "number") return `${event.price} €`;
  return "Precio por confirmar";
}

export function placeLabel(event: EventCandidate): string {
  return event.municipality || event.venue_name || event.address || "Lugar por confirmar";
}

export function primaryTag(event: EventCandidate): string {
  return event.category || event.tags?.[0] || "Plan";
}

export function sourceLabel(event: EventCandidate): string {
  return event.source_name || "Fuente pública";
}
