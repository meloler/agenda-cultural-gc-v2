import { describe, expect, it } from "vitest";
import { assignCollections, scoreEvent } from "@agenda-cultural-gc/event-intelligence";
import { buildCollectionsFromEvents } from "../get-home-events";
import { mapSupabaseEvent, type SupabaseEventRow } from "../map-supabase-event";
import { getPublicSupabaseConfig } from "../source";

const context = { now: "2026-06-12T10:00:00.000Z" };

function row(overrides: Partial<SupabaseEventRow> = {}): SupabaseEventRow {
  return {
    id: "real-1",
    nombre: "Concierto familiar real",
    lugar: "Parque Doramas",
    fecha_iso: "2026-06-12",
    hora: "20:00",
    descripcion: "Concierto al aire libre para familias con música en directo.",
    estilo: "Música",
    imagen_url: "https://example.com/real.jpg",
    source_id: "Fuente pública",
    url_venta: "https://example.com/real",
    precio_num: 0,
    latitud: 28.12,
    longitud: -15.43,
    created_at: "2026-06-01T10:00:00.000Z",
    updated_at: "2026-06-01T10:00:00.000Z",
    ...overrides,
  };
}

describe("Supabase event source mapping", () => {
  it("maps a Supabase event row to the Event Intelligence model", () => {
    const event = mapSupabaseEvent(row());

    expect(event.id).toBe("real-1");
    expect(event.title).toBe("Concierto familiar real");
    expect(event.starts_at).toBe("2026-06-12T20:00:00");
    expect(event.category).toBe("Música");
    expect(event.is_free).toBe(true);
    expect(event.source_url).toBe("https://example.com/real");
  });

  it("excludes Supabase events without valid date from generated collections", () => {
    const event = mapSupabaseEvent(row({ fecha_iso: "sin fecha" }));
    const collections = buildCollectionsFromEvents([event], context);

    expect(collections).toEqual([]);
  });

  it("detects missing Supabase public configuration for controlled fallback", () => {
    const config = getPublicSupabaseConfig({});

    expect(config.configured).toBe(false);
  });

  it("generates home collections through Event Intelligence", () => {
    const event = mapSupabaseEvent(row());
    const directCollections = assignCollections(event, context).map((collection) => collection.id);
    const homeCollections = buildCollectionsFromEvents([event], context).map((collection) => collection.id);

    expect(homeCollections).toEqual(expect.arrayContaining(directCollections));
  });

  it("sorts simulated real events by descending score", () => {
    const complete = mapSupabaseEvent(row({ id: "complete" }));
    const incomplete = mapSupabaseEvent(row({ id: "incomplete", imagen_url: null, precio_num: null, latitud: null, longitud: null }));
    const collections = buildCollectionsFromEvents([incomplete, complete], context);
    const today = collections.find((collection) => collection.id === "top-today");

    expect(today?.events.map((item) => item.score)).toEqual(
      [...(today?.events.map((item) => item.score) ?? [])].sort((a, b) => b - a),
    );
    expect(scoreEvent(complete, context).score).toBeGreaterThan(scoreEvent(incomplete, context).score);
  });
});
