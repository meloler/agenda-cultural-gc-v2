import { describe, expect, it } from "vitest";
import { buildHomeCollections, intentChips } from "../collections";
import { mockEvents } from "../mock-events";

describe("home collection presentation", () => {
  it("excludes non-publishable mock events", () => {
    const collections = buildHomeCollections();
    const visibleIds = collections.flatMap((collection) => collection.events.map((item) => item.event.id));

    expect(visibleIds).not.toContain("mock-no-publicable");
  });

  it("has mock events in at least five MVP collections", () => {
    const collections = buildHomeCollections();

    expect(collections.length).toBeGreaterThanOrEqual(5);
  });

  it("sorts events by descending score inside each collection", () => {
    const collections = buildHomeCollections();

    for (const collection of collections) {
      const scores = collection.events.map((item) => item.score);
      const sorted = [...scores].sort((a, b) => b - a);
      expect(scores).toEqual(sorted);
    }
  });

  it("keeps the main intent chips available", () => {
    expect(intentChips).toEqual(expect.arrayContaining(["Hoy", "Este finde", "Cerca de mí", "Gratis", "Con niños"]));
  });

  it("uses the expected mock data set", () => {
    expect(mockEvents.length).toBeGreaterThanOrEqual(7);
  });
});
