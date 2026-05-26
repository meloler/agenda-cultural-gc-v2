import type { EventCandidate, EventIntelligenceContext, ScoreResult } from "./types";
import {
  getEventQualityIssues,
  hasCategoryOrTags,
  hasClearLocation,
  hasCoordinates,
  hasDefinedPrice,
  hasReliableLink,
  hasSourceOrLink,
  hasText,
  hasTime,
  hasUsefulTags,
  hasValidImage,
  normalizeText,
  parseEventDate,
} from "./quality";

const DAY_MS = 24 * 60 * 60 * 1000;

function startOfDay(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

export function daysUntil(eventDate: Date, now: Date): number {
  return Math.round((startOfDay(eventDate).getTime() - startOfDay(now).getTime()) / DAY_MS);
}

export function isSameCalendarDay(a: Date, b: Date): boolean {
  return startOfDay(a).getTime() === startOfDay(b).getTime();
}

export function isPastEvent(eventDate: Date, now: Date): boolean {
  return daysUntil(eventDate, now) < 0;
}

export function isInUpcomingWeekend(eventDate: Date, now: Date): boolean {
  const day = now.getDay();
  const toSaturday = day === 6 ? 0 : day === 0 ? -1 : 6 - day;
  const saturday = new Date(startOfDay(now).getTime() + toSaturday * DAY_MS);
  const sunday = new Date(saturday.getTime() + DAY_MS);
  const eventDay = startOfDay(eventDate).getTime();
  return eventDay === saturday.getTime() || eventDay === sunday.getTime();
}

function hasDuplicateSignal(event: EventCandidate): boolean {
  return (event.tags ?? []).some((tag) => {
    const normalized = normalizeText(tag);
    return normalized.includes("duplicate") || normalized.includes("duplicado") || normalized.includes("posible duplicado");
  });
}

function hasPreferredSignal(event: EventCandidate, context: EventIntelligenceContext): boolean {
  const preferredTags = context.preferredTags ?? [];
  if (preferredTags.length === 0) return false;
  const text = normalizeText([event.category, ...(event.tags ?? [])].join(" "));
  return preferredTags.some((tag) => text.includes(normalizeText(tag)));
}

export function scoreEvent(event: EventCandidate, context: EventIntelligenceContext): ScoreResult {
  const now = new Date(context.now);
  const start = parseEventDate(event.starts_at);
  const positive: string[] = [];
  const negative: string[] = [];
  let score = 0;

  if (!start || Number.isNaN(now.getTime())) {
    return {
      score: 0,
      positive,
      negative: ["No se puede priorizar porque falta una fecha valida"],
    };
  }

  if (isSameCalendarDay(start, now)) {
    score += 30;
    positive.push("Ocurre hoy");
  }

  if (isInUpcomingWeekend(start, now)) {
    score += 18;
    positive.push("Encaja en el fin de semana proximo");
  }

  const distanceDays = daysUntil(start, now);
  if (distanceDays >= 0 && distanceDays <= 7) {
    score += 10;
    positive.push("Fecha cercana");
  } else if (distanceDays > 7 && distanceDays <= 30) {
    score += 4;
    positive.push("Fecha proxima");
  }

  if (hasValidImage(event)) {
    score += 8;
    positive.push("Tiene imagen util");
  }

  if (hasClearLocation(event)) {
    score += 8;
    positive.push("Tiene ubicacion clara");
  }

  if (hasDefinedPrice(event)) {
    score += 6;
    positive.push(event.is_free ? "Indica que es gratis" : "Tiene precio definido");
  }

  if (hasCategoryOrTags(event)) {
    score += 5;
    positive.push("Tiene categoria clara");
  }

  if (hasUsefulTags(event)) {
    score += 5;
    positive.push("Tiene etiquetas utiles");
  }

  if (hasReliableLink(event)) {
    score += 5;
    positive.push("Tiene enlace fiable");
  }

  if (hasText(event.source_name)) {
    score += 4;
    positive.push("Tiene fuente identificada");
  }

  if (context.preferredMunicipality && normalizeText(event.municipality) === normalizeText(context.preferredMunicipality)) {
    score += 5;
    positive.push("Coincide con el municipio preferido");
  }

  if (hasPreferredSignal(event, context)) {
    score += 4;
    positive.push("Coincide con intereses preferidos");
  }

  if (!hasTime(event.starts_at)) {
    score -= 4;
    negative.push("Falta hora");
  }

  if (!hasValidImage(event)) {
    score -= 5;
    negative.push("Falta imagen");
  }

  if (!hasText(event.description)) {
    score -= 4;
    negative.push("Falta descripcion");
  }

  if (!hasDefinedPrice(event)) {
    score -= 4;
    negative.push("Falta precio");
  }

  if (!hasClearLocation(event) || !hasCoordinates(event)) {
    score -= 5;
    negative.push("Ubicacion incompleta");
  }

  if (!hasSourceOrLink(event) || !hasReliableLink(event)) {
    score -= 5;
    negative.push("Fuente incompleta");
  }

  if (isPastEvent(start, now)) {
    score -= 40;
    negative.push("Fecha pasada");
  }

  if (hasDuplicateSignal(event)) {
    score -= 15;
    negative.push("Posible duplicado");
  }

  for (const issue of getEventQualityIssues(event)) {
    if (issue === "Falta fecha valida") score -= 30;
  }

  return { score: Math.max(0, Math.round(score)), positive, negative };
}
