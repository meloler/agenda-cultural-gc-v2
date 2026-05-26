import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { EventCard } from "../EventCard";
import { buildHomeCollections } from "../../lib/collections";

describe("EventCard navigation", () => {
  it("links cards to /events/[id]", () => {
    const item = buildHomeCollections().flatMap((collection) => collection.events)[0];
    const html = renderToStaticMarkup(<EventCard item={item} />);

    expect(html).toContain(`href="/events/${item.event.id}"`);
  });
});
