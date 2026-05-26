import type { EventCandidate, EventIntelligenceContext } from "@agenda-cultural-gc/event-intelligence";
import { buildHomeCollections, defaultHomeContext, type HomeCollection } from "../collections";
import { mockEvents } from "../mock-events";
import { fetchSupabaseEvents } from "./supabase";

export interface HomeEventsResult {
  collections: HomeCollection[];
  source: "supabase" | "mock";
  warning?: string;
}

export function buildCollectionsFromEvents(events: EventCandidate[], context: EventIntelligenceContext): HomeCollection[] {
  return buildHomeCollections(events, context);
}

export async function getHomeEvents(): Promise<HomeEventsResult> {
  const now = new Date();
  const sourceResult = await fetchSupabaseEvents(now);

  if (sourceResult.kind === "supabase" && sourceResult.events.length > 0) {
    return {
      collections: buildCollectionsFromEvents(sourceResult.events, { now }),
      source: "supabase",
    };
  }

  return {
    collections: buildCollectionsFromEvents(mockEvents, defaultHomeContext),
    source: "mock",
    warning: sourceResult.warning ?? "No hay eventos reales publicables; usando eventos mock.",
  };
}
