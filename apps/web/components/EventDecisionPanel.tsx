import type { EventCandidate } from "@agenda-cultural-gc/event-intelligence";
import { formatDate, formatTime, placeLabel, priceLabel, sourceLabel } from "../lib/events/presentation";
import { SafeExternalLink } from "./SafeExternalLink";

export function EventDecisionPanel({ event }: { event: EventCandidate }) {
  const time = formatTime(event.starts_at);

  return (
    <section className="decision-panel" aria-labelledby="decision-title">
      <h2 id="decision-title">Lo esencial para decidir</h2>
      <dl>
        <div>
          <dt>Cuándo</dt>
          <dd>{formatDate(event.starts_at)}{time ? ` · ${time}` : ""}</dd>
        </div>
        <div>
          <dt>Dónde</dt>
          <dd>{placeLabel(event)}</dd>
        </div>
        {event.address ? (
          <div>
            <dt>Dirección</dt>
            <dd>{event.address}</dd>
          </div>
        ) : null}
        <div>
          <dt>Precio</dt>
          <dd>{priceLabel(event)}</dd>
        </div>
        <div>
          <dt>Fuente</dt>
          <dd>{sourceLabel(event)}</dd>
        </div>
      </dl>
      <SafeExternalLink className="detail-cta" href={event.source_url}>
        Ver información oficial
      </SafeExternalLink>
    </section>
  );
}
