import {
  assignCollections,
  explainEventRanking,
  isPublishableEvent,
  scoreEvent,
  type CollectionId,
  type EventCandidate,
  type EventIntelligenceContext,
} from "@agenda-cultural-gc/event-intelligence";
import { MOCK_NOW, mockEvents } from "./mock-events";

export const collectionOrder: CollectionId[] = [
  "top-today",
  "weekend",
  "free-or-cheap",
  "family",
  "live-music",
  "stage",
  "markets-fairs",
  "hidden-gems",
];

export const collectionTitles: Record<CollectionId, string> = {
  "top-today": "Top planes de hoy",
  weekend: "Este finde",
  "free-or-cheap": "Gratis o baratos",
  family: "Con niños",
  "live-music": "Música en directo",
  stage: "Teatro y escena",
  "markets-fairs": "Mercadillos y ferias",
  "hidden-gems": "Joyas escondidas",
};

export interface HomeEvent {
  event: EventCandidate;
  score: number;
  reasons: string[];
  signal: string;
}

export interface HomeCollection {
  id: CollectionId;
  title: string;
  events: HomeEvent[];
}

export const intentChips = [
  "Hoy",
  "Este finde",
  "Cerca de mí",
  "Gratis",
  "Con niños",
  "Música",
  "Teatro",
  "Mercadillos",
  "Al aire libre",
  "Noche",
  "Algo diferente",
];

export const defaultHomeContext: EventIntelligenceContext = {
  now: MOCK_NOW,
};

function editorialSignal(event: EventCandidate, collectionId: CollectionId, reasons: string[]): string {
  if (event.is_free) return "Gratis";
  if (collectionId === "family") return "Buen plan familiar";
  if (collectionId === "hidden-gems") return "Joyita local";
  if (reasons.some((reason) => reason.includes("Ocurre hoy"))) return "Para hoy";
  if (collectionId === "weekend") return "Modo finde";
  return "Plan destacado";
}

export function buildHomeCollections(
  events: EventCandidate[] = mockEvents,
  context: EventIntelligenceContext = defaultHomeContext,
): HomeCollection[] {
  const buckets = new Map<CollectionId, HomeEvent[]>();

  for (const event of events) {
    if (!isPublishableEvent(event)) continue;

    const collections = assignCollections(event, context);
    const score = scoreEvent(event, context).score;
    const explanation = explainEventRanking(event, context);

    for (const collection of collections) {
      const item: HomeEvent = {
        event,
        score,
        reasons: explanation.reasons.slice(0, 2),
        signal: editorialSignal(event, collection.id, explanation.reasons),
      };
      buckets.set(collection.id, [...(buckets.get(collection.id) ?? []), item]);
    }
  }

  return collectionOrder
    .map((id) => ({
      id,
      title: collectionTitles[id],
      events: (buckets.get(id) ?? []).sort((a, b) => b.score - a.score),
    }))
    .filter((collection) => collection.events.length > 0);
}

export function getHeroStats(collections: HomeCollection[]): { collectionCount: number; eventCount: number } {
  const eventIds = new Set<string>();
  for (const collection of collections) {
    for (const item of collection.events) eventIds.add(item.event.id);
  }
  return {
    collectionCount: collections.length,
    eventCount: eventIds.size,
  };
}
