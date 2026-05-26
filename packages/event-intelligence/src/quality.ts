import type { EventCandidate } from "./types";

const BLOCKING_ISSUES = new Set([
  "Falta titulo",
  "Falta fecha valida",
  "Falta ubicacion clara",
  "Falta categoria o tags",
  "Falta fuente o enlace",
]);

export function hasText(value: string | null | undefined): boolean {
  return typeof value === "string" && value.trim().length > 0;
}

export function parseEventDate(value: string | null | undefined): Date | null {
  if (!hasText(value)) return null;
  const parsed = new Date(value as string);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export function hasTime(value: string | null | undefined): boolean {
  if (!hasText(value)) return false;
  return /T\d{2}:\d{2}|\s\d{2}:\d{2}/.test(value as string);
}

export function hasClearLocation(event: EventCandidate): boolean {
  return hasText(event.venue_name) || hasText(event.address) || hasText(event.municipality);
}

export function hasCoordinates(event: EventCandidate): boolean {
  return typeof event.latitude === "number" && typeof event.longitude === "number";
}

export function hasCategoryOrTags(event: EventCandidate): boolean {
  return hasText(event.category) || Boolean(event.tags?.some(hasText));
}

export function hasSourceOrLink(event: EventCandidate): boolean {
  return hasText(event.source_name) || hasText(event.source_url);
}

export function hasReliableLink(event: EventCandidate): boolean {
  if (!hasText(event.source_url)) return false;
  try {
    const url = new URL(event.source_url as string);
    return url.protocol === "https:" || url.protocol === "http:";
  } catch {
    return false;
  }
}

export function hasValidImage(event: EventCandidate): boolean {
  if (!hasText(event.image_url)) return false;
  const image = (event.image_url as string).trim().toLowerCase();
  if (image.startsWith("data:")) return false;
  if (image.includes("placeholder") || image.includes("transparent")) return false;
  return image.startsWith("http://") || image.startsWith("https://");
}

export function hasUsefulTags(event: EventCandidate): boolean {
  return Boolean(event.tags?.some((tag) => hasText(tag) && tag.trim().length >= 3));
}

export function hasDefinedPrice(event: EventCandidate): boolean {
  return event.is_free === true || typeof event.price === "number";
}

export function normalizeText(value: string | null | undefined): string {
  return (value ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

export function searchableText(event: EventCandidate): string {
  return normalizeText([
    event.title,
    event.description,
    event.category,
    event.venue_name,
    event.municipality,
    ...(event.tags ?? []),
  ].filter(Boolean).join(" "));
}

export function getEventQualityIssues(event: EventCandidate): string[] {
  const issues: string[] = [];

  if (!hasText(event.title)) issues.push("Falta titulo");
  if (!parseEventDate(event.starts_at)) issues.push("Falta fecha valida");
  if (!hasClearLocation(event)) issues.push("Falta ubicacion clara");
  if (!hasCategoryOrTags(event)) issues.push("Falta categoria o tags");
  if (!hasSourceOrLink(event)) issues.push("Falta fuente o enlace");

  if (!hasTime(event.starts_at)) issues.push("Falta hora");
  if (!hasValidImage(event)) issues.push("Falta imagen");
  if (!hasText(event.description)) issues.push("Falta descripcion");
  if (!hasDefinedPrice(event)) issues.push("Falta precio");
  if (!hasCoordinates(event)) issues.push("Faltan coordenadas");

  return issues;
}

export function isPublishableEvent(event: EventCandidate): boolean {
  return getEventQualityIssues(event).every((issue) => !BLOCKING_ISSUES.has(issue));
}
