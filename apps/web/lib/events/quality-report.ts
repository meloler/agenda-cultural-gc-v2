import type { EventCandidate, EventIntelligenceContext } from "@agenda-cultural-gc/event-intelligence";
import { getEventQualityIssues, isPublishableEvent, scoreEvent } from "@agenda-cultural-gc/event-intelligence";

export interface EventQualityReport {
  total: number;
  publishable: number;
  rejected: number;
  pastEvents: number;
  incompleteButPublishable: number;
  missingOfficialUrl: number;
  issueCounts: Record<string, number>;
}

function eventDate(value: string | null | undefined): Date | null {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function isPast(event: EventCandidate, context: EventIntelligenceContext): boolean {
  const start = eventDate(event.starts_at);
  const now = new Date(context.now);
  if (!start || Number.isNaN(now.getTime())) return false;
  const eventDay = new Date(start.getFullYear(), start.getMonth(), start.getDate()).getTime();
  const nowDay = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  return eventDay < nowDay;
}

export function createEventQualityReport(events: EventCandidate[], context: EventIntelligenceContext): EventQualityReport {
  const issueCounts: Record<string, number> = {};
  let publishable = 0;
  let pastEvents = 0;
  let incompleteButPublishable = 0;
  let missingOfficialUrl = 0;

  for (const event of events) {
    const issues = getEventQualityIssues(event);
    const canPublish = isPublishableEvent(event);

    for (const issue of issues) {
      issueCounts[issue] = (issueCounts[issue] ?? 0) + 1;
    }

    if (canPublish) publishable += 1;
    if (isPast(event, context)) pastEvents += 1;
    if (canPublish && issues.length > 0) incompleteButPublishable += 1;
    if (!event.source_url) missingOfficialUrl += 1;

    // Keep score calculation exercised by QA report consumers without changing ranking rules.
    scoreEvent(event, context);
  }

  return {
    total: events.length,
    publishable,
    rejected: events.length - publishable,
    pastEvents,
    incompleteButPublishable,
    missingOfficialUrl,
    issueCounts,
  };
}
