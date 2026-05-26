import type { EventCandidate, EventIntelligenceContext } from "@agenda-cultural-gc/event-intelligence";
import { isPublishableEvent } from "@agenda-cultural-gc/event-intelligence";
import { defaultHomeContext } from "../collections";
import { mockEvents } from "../mock-events";
import { fetchSupabaseEvents } from "./supabase";

export interface CuratedEventsResult {
  events: EventCandidate[];
  source: "supabase" | "mock";
  warning?: string;
  context: EventIntelligenceContext;
}

export async function getCuratedEvents(): Promise<CuratedEventsResult> {
  const now = new Date();
  const sourceResult = await fetchSupabaseEvents(now);

  if (sourceResult.kind === "supabase" && sourceResult.events.length > 0) {
    return {
      events: sourceResult.events,
      source: "supabase",
      context: { now },
    };
  }

  return {
    events: mockEvents,
    source: "mock",
    warning: sourceResult.warning ?? "No hay eventos reales publicables; usando eventos mock.",
    context: defaultHomeContext,
  };
}

export async function getEventById(id: string): Promise<
  | { status: "found"; event: EventCandidate; source: "supabase" | "mock"; warning?: string; context: EventIntelligenceContext }
  | { status: "not-found"; source: "supabase" | "mock"; warning?: string }
  | { status: "not-publishable"; source: "supabase" | "mock"; warning?: string }
> {
  const result = await getCuratedEvents();
  const event = result.events.find((candidate) => candidate.id === id);

  if (!event) {
    return { status: "not-found", source: result.source, warning: result.warning };
  }

  if (!isPublishableEvent(event)) {
    return { status: "not-publishable", source: result.source, warning: result.warning };
  }

  return {
    status: "found",
    event,
    source: result.source,
    warning: result.warning,
    context: result.context,
  };
}
