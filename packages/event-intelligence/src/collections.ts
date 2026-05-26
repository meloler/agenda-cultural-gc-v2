import type { CollectionAssignment, EventCandidate, EventIntelligenceContext } from "./types";
import { isPublishableEvent, searchableText } from "./quality";
import { isInUpcomingWeekend, isPastEvent, isSameCalendarDay, scoreEvent } from "./scoring";
import { parseEventDate, normalizeText } from "./quality";

const CHEAP_PRICE_EUR = 10;

const COLLECTIONS = {
  today: { id: "top-today", title: "Top planes de hoy" },
  weekend: { id: "weekend", title: "Este finde" },
  cheap: { id: "free-or-cheap", title: "Gratis o baratos" },
  family: { id: "family", title: "Con ninos" },
  music: { id: "live-music", title: "Musica en directo" },
  stage: { id: "stage", title: "Teatro y escena" },
  markets: { id: "markets-fairs", title: "Mercadillos y ferias" },
  hidden: { id: "hidden-gems", title: "Joyas escondidas" },
} as const;

function includesAny(text: string, keywords: string[]): boolean {
  return keywords.some((keyword) => text.includes(normalizeText(keyword)));
}

function isCheapOrFree(event: EventCandidate): boolean {
  return event.is_free === true || (typeof event.price === "number" && event.price <= CHEAP_PRICE_EUR);
}

function isHiddenGem(event: EventCandidate, context: EventIntelligenceContext): boolean {
  const score = scoreEvent(event, context).score;
  const text = searchableText(event);
  const source = normalizeText(event.source_name);
  const hasLocalSignal = includesAny(text, ["barrio", "local", "independiente", "pequeno formato", "pequena sala", "centro civico"]);
  const mainstreamSource = includesAny(source, ["ticketmaster", "entradas", "tomaticket", "auditorio", "teatro perez galdos", "infecar"]);
  return score >= 35 && (hasLocalSignal || !mainstreamSource);
}

export function assignCollections(event: EventCandidate, context: EventIntelligenceContext): CollectionAssignment[] {
  if (!isPublishableEvent(event)) return [];
  const start = parseEventDate(event.starts_at);
  const now = new Date(context.now);
  if (!start || Number.isNaN(now.getTime()) || isPastEvent(start, now)) return [];

  const text = searchableText(event);
  const assignments: CollectionAssignment[] = [];

  if (isSameCalendarDay(start, now)) {
    assignments.push({ ...COLLECTIONS.today, reason: "Ocurre hoy y es publicable" });
  }

  if (isInUpcomingWeekend(start, now)) {
    assignments.push({ ...COLLECTIONS.weekend, reason: "Ocurre sabado o domingo del proximo fin de semana" });
  }

  if (isCheapOrFree(event)) {
    assignments.push({ ...COLLECTIONS.cheap, reason: "Es gratis o tiene precio bajo" });
  }

  if (includesAny(text, ["familiar", "familia", "infantil", "ninos", "ninas", "peques", "cuentacuentos", "titeres"])) {
    assignments.push({ ...COLLECTIONS.family, reason: "Tiene senales familiares o infantiles" });
  }

  if (includesAny(text, ["musica", "concierto", "live music", "directo", "jazz", "rock", "festival", "cantautor"])) {
    assignments.push({ ...COLLECTIONS.music, reason: "Tiene senales de musica en directo" });
  }

  if (includesAny(text, ["teatro", "danza", "escena", "artes escenicas", "ballet", "opera", "monologo", "comedia"])) {
    assignments.push({ ...COLLECTIONS.stage, reason: "Tiene senales de teatro, danza o escena" });
  }

  if (includesAny(text, ["mercadillo", "feria", "market", "artesania", "artesanal", "muestra", "rastro"])) {
    assignments.push({ ...COLLECTIONS.markets, reason: "Tiene senales de mercado, feria o artesania" });
  }

  if (isHiddenGem(event, context)) {
    assignments.push({ ...COLLECTIONS.hidden, reason: "Tiene buena calidad y senales menos masivas" });
  }

  return assignments;
}
