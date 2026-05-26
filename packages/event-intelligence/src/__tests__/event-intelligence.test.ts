import { describe, expect, it } from "vitest";
import {
  assignCollections,
  explainEventRanking,
  isPublishableEvent,
  scoreEvent,
  type EventCandidate,
  type EventIntelligenceContext,
} from "../index";

const context: EventIntelligenceContext = {
  now: "2026-06-12T10:00:00.000Z", // Friday
};

function event(overrides: Partial<EventCandidate> = {}): EventCandidate {
  return {
    id: "evt-1",
    title: "Concierto familiar en el parque",
    description: "Un plan cultural completo para disfrutar en Gran Canaria.",
    starts_at: "2026-06-12T20:00:00.000Z",
    ends_at: "2026-06-12T22:00:00.000Z",
    venue_name: "Parque San Telmo",
    municipality: "Las Palmas de Gran Canaria",
    address: "Calle Mayor de Triana",
    latitude: 28.123,
    longitude: -15.43,
    category: "Musica",
    tags: ["concierto", "familia", "directo"],
    price: 0,
    is_free: true,
    image_url: "https://example.com/event.jpg",
    source_name: "Agenda Cultural GC",
    source_url: "https://example.com/evento",
    created_at: "2026-06-01T10:00:00.000Z",
    updated_at: "2026-06-01T10:00:00.000Z",
    ...overrides,
  };
}

function ids(events: ReturnType<typeof assignCollections>): string[] {
  return events.map((collection) => collection.id);
}

describe("Event Intelligence", () => {
  it("marks a complete event as publishable", () => {
    expect(isPublishableEvent(event())).toBe(true);
  });

  it("does not publish an event without a valid date", () => {
    expect(isPublishableEvent(event({ starts_at: "sin fecha" }))).toBe(false);
  });

  it("does not publish an event without title", () => {
    expect(isPublishableEvent(event({ title: "   " }))).toBe(false);
  });

  it("assigns today's event to Top planes de hoy", () => {
    expect(ids(assignCollections(event(), context))).toContain("top-today");
  });

  it("assigns a weekend event to Este finde", () => {
    const saturdayEvent = event({ starts_at: "2026-06-13T20:00:00.000Z" });
    expect(ids(assignCollections(saturdayEvent, context))).toContain("weekend");
  });

  it("assigns a free event to Gratis o baratos", () => {
    expect(ids(assignCollections(event({ is_free: true, price: 0 }), context))).toContain("free-or-cheap");
  });

  it("assigns family tags to Con ninos", () => {
    const familyEvent = event({ category: "Infantil", tags: ["ninos", "familia"] });
    expect(ids(assignCollections(familyEvent, context))).toContain("family");
  });

  it("assigns music events to Musica en directo", () => {
    const musicEvent = event({ category: "Concierto", tags: ["jazz", "directo"] });
    expect(ids(assignCollections(musicEvent, context))).toContain("live-music");
  });

  it("assigns theatre events to Teatro y escena", () => {
    const theatreEvent = event({ category: "Teatro", tags: ["artes escenicas"] });
    expect(ids(assignCollections(theatreEvent, context))).toContain("stage");
  });

  it("assigns market events to Mercadillos y ferias", () => {
    const marketEvent = event({ category: "Feria", tags: ["mercadillo", "artesania"] });
    expect(ids(assignCollections(marketEvent, context))).toContain("markets-fairs");
  });

  it("scores incomplete events below complete events", () => {
    const completeScore = scoreEvent(event(), context).score;
    const incompleteScore = scoreEvent(
      event({ description: null, image_url: null, price: null, is_free: null, latitude: null, longitude: null }),
      context,
    ).score;

    expect(incompleteScore).toBeLessThan(completeScore);
  });

  it("returns readable ranking reasons", () => {
    const explanation = explainEventRanking(event(), context);
    expect(explanation.score).toBeGreaterThan(0);
    expect(explanation.reasons.length).toBeGreaterThan(0);
    expect(explanation.reasons.some((reason) => reason.includes("Suma:"))).toBe(true);
  });

  it("keeps scoring stable for the same input", () => {
    const first = scoreEvent(event(), context);
    const second = scoreEvent(event(), context);
    expect(second).toEqual(first);
  });

  it("does not prioritize a past event", () => {
    const pastEvent = event({ starts_at: "2026-06-01T20:00:00.000Z" });
    expect(assignCollections(pastEvent, context)).toEqual([]);
    expect(scoreEvent(pastEvent, context).score).toBeLessThan(scoreEvent(event(), context).score);
  });
});
