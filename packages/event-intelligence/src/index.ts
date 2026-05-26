import type { EventCandidate, EventIntelligenceContext, RankingExplanation } from "./types";
import { assignCollections } from "./collections";
import { getEventQualityIssues, isPublishableEvent } from "./quality";
import { scoreEvent } from "./scoring";

export type {
  CollectionAssignment,
  CollectionId,
  EventCandidate,
  EventIntelligenceContext,
  RankingExplanation,
  ScoreResult,
} from "./types";

export { assignCollections } from "./collections";
export { getEventQualityIssues, isPublishableEvent } from "./quality";
export { scoreEvent } from "./scoring";

export function explainEventRanking(event: EventCandidate, context: EventIntelligenceContext): RankingExplanation {
  const scoring = scoreEvent(event, context);
  const issues = getEventQualityIssues(event);
  const collections = assignCollections(event, context);
  const reasons = [
    ...scoring.positive.map((reason) => `Suma: ${reason}`),
    ...scoring.negative.map((reason) => `Resta: ${reason}`),
  ];

  if (!isPublishableEvent(event)) {
    reasons.unshift("No entra en colecciones publicas porque no cumple los minimos de publicacion");
  }

  return {
    score: scoring.score,
    reasons,
    issues,
    collections,
  };
}
