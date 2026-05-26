import { createClient } from "@supabase/supabase-js";
import type { EventCandidate } from "@agenda-cultural-gc/event-intelligence";
import { mapSupabaseEvent, type SupabaseEventRow } from "./map-supabase-event";
import { getPublicSupabaseConfig, type EventSourceResult } from "./source";

const EVENT_SELECT = [
  "id",
  "nombre",
  "lugar",
  "fecha_iso",
  "hora",
  "descripcion",
  "estilo",
  "imagen_url",
  "source_id",
  "url_venta",
  "precio_num",
  "latitud",
  "longitud",
  "created_at",
  "updated_at",
].join(", ");

export async function fetchSupabaseEvents(now = new Date()): Promise<EventSourceResult<EventCandidate>> {
  const config = getPublicSupabaseConfig();
  if (!config.configured) {
    return {
      kind: "mock",
      events: [],
      warning: "Supabase no está configurado; usando eventos mock.",
    };
  }

  const supabase = createClient(config.url, config.anonKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  });

  const today = now.toISOString().slice(0, 10);
  const { data, error } = await supabase
    .from("evento")
    .select(EVENT_SELECT)
    .not("fecha_iso", "is", null)
    .gte("fecha_iso", today)
    .order("fecha_iso", { ascending: true })
    .limit(120);

  if (error) {
    return {
      kind: "mock",
      events: [],
      warning: "No se pudieron cargar eventos reales; usando eventos mock.",
    };
  }

  const rows = (data ?? []) as unknown as SupabaseEventRow[];

  return {
    kind: "supabase",
    events: rows.map(mapSupabaseEvent),
  };
}
