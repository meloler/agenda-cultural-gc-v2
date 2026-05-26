import { describe, expect, it } from "vitest";
import { scoreEvent, type EventCandidate } from "@agenda-cultural-gc/event-intelligence";
import { buildHomeCollections } from "../collections";
import { MOCK_NOW, mockEvents } from "../mock-events";
import { createEventQualityReport } from "../events/quality-report";

const context = { now: MOCK_NOW };

function minimalEvent(overrides: Partial<EventCandidate> = {}): EventCandidate {
  return {
    id: "minimal",
    title: "Plan mínimo publicable",
    description: null,
    starts_at: "2026-06-13T19:00:00.000Z",
    ends_at: null,
    venue_name: "Plaza pública",
    municipality: null,
    address: null,
    latitude: null,
    longitude: null,
    category: "Música",
    tags: null,
    price: null,
    is_free: null,
    image_url: null,
    source_name: "Fuente mínima",
    source_url: null,
    created_at: null,
    updated_at: null,
    ...overrides,
  };
}

describe("event quality hardening", () => {
  it("does not prioritize past events over upcoming events", () => {
    const upcoming = minimalEvent({ id: "upcoming", starts_at: "2026-06-13T19:00:00.000Z" });
    const past = minimalEvent({ id: "past", starts_at: "2026-06-01T19:00:00.000Z" });

    expect(scoreEvent(past, context).score).toBeLessThan(scoreEvent(upcoming, context).score);
    expect(buildHomeCollections([past, upcoming], context).flatMap((collection) => collection.events.map((item) => item.event.id))).not.toContain("past");
  });

  it("does not break when collection generation receives an empty list", () => {
    expect(buildHomeCollections([], context)).toEqual([]);
  });

  it("does not break with optional fields missing when minimum publishable data exists", () => {
    const collections = buildHomeCollections([minimalEvent()], context);

    expect(collections.length).toBeGreaterThan(0);
  });

  it("creates a local event quality report", () => {
    const report = createEventQualityReport(mockEvents, context);

    expect(report.total).toBe(mockEvents.length);
    expect(report.rejected).toBeGreaterThan(0);
    expect(report.issueCounts["Falta fecha valida"]).toBeGreaterThan(0);
  });
});
