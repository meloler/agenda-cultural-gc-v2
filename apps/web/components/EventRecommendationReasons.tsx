import type { EventCandidate, EventIntelligenceContext } from "@agenda-cultural-gc/event-intelligence";
import { explainEventRanking } from "@agenda-cultural-gc/event-intelligence";

function cleanReason(reason: string): string {
  return reason.replace(/^Suma: /, "").replace(/^Resta: /, "Pendiente: ");
}

export function getRecommendationReasons(event: EventCandidate, context: EventIntelligenceContext): string[] {
  return explainEventRanking(event, context).reasons.map(cleanReason).slice(0, 4);
}

export function EventRecommendationReasons({ event, context }: { event: EventCandidate; context: EventIntelligenceContext }) {
  const reasons = getRecommendationReasons(event, context);

  return (
    <section className="recommendation" aria-labelledby="recommendation-title">
      <h2 id="recommendation-title">Por qué aparece destacado</h2>
      <ul>
        {reasons.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>
    </section>
  );
}
