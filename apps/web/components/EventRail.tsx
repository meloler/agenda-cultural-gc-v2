import type { HomeCollection } from "../lib/collections";
import { EventCard } from "./EventCard";

export function EventRail({ collection }: { collection: HomeCollection }) {
  if (collection.events.length === 0) return null;

  return (
    <section className="rail" aria-labelledby={`rail-${collection.id}`}>
      <div className="rail__header">
        <h2 id={`rail-${collection.id}`}>{collection.title}</h2>
        <span>{collection.events.length} planes</span>
      </div>
      <div className="rail__scroller" role="list" aria-label={collection.title}>
        {collection.events.map((item) => (
          <div role="listitem" key={`${collection.id}-${item.event.id}`}>
            <EventCard item={item} />
          </div>
        ))}
      </div>
    </section>
  );
}
