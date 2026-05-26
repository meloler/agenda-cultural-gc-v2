import { describe, expect, it } from "vitest";
import { getEventById } from "../get-event-by-id";

describe("getEventById", () => {
  it("returns an existing publishable event", async () => {
    const result = await getEventById("mock-hoy-jazz");

    expect(result.status).toBe("found");
    if (result.status === "found") {
      expect(result.event.title).toBe("Jazz al atardecer en San Telmo");
    }
  });

  it("does not return non-publishable events as valid detail pages", async () => {
    const result = await getEventById("mock-no-publicable");

    expect(result.status).toBe("not-publishable");
  });

  it("returns not-found for unknown ids", async () => {
    const result = await getEventById("missing-event");

    expect(result.status).toBe("not-found");
  });
});
