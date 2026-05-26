import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { EventDecisionPanel } from "../EventDecisionPanel";
import { EventRecommendationReasons, getRecommendationReasons } from "../EventRecommendationReasons";
import { mockEvents, MOCK_NOW } from "../../lib/mock-events";

const event = mockEvents.find((candidate) => candidate.id === "mock-hoy-jazz");

describe("event detail presentation", () => {
  it("shows title-adjacent decision data for a valid event", () => {
    if (!event) throw new Error("Missing mock event");
    const html = renderToStaticMarkup(<EventDecisionPanel event={event} />);

    expect(html).toContain("viernes");
    expect(html).toContain("Parque San Telmo");
    expect(html).toContain("Gratis");
  });

  it("uses Event Intelligence reasons", () => {
    if (!event) throw new Error("Missing mock event");
    const reasons = getRecommendationReasons(event, { now: MOCK_NOW });
    const html = renderToStaticMarkup(<EventRecommendationReasons event={event} context={{ now: MOCK_NOW }} />);

    expect(reasons.length).toBeGreaterThan(0);
    expect(html).toContain(reasons[0]);
  });
});
