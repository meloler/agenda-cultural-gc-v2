import type { EventCandidate } from "@agenda-cultural-gc/event-intelligence";

export interface SupabaseEventRow {
  id: string | number;
  nombre?: string | null;
  lugar?: string | null;
  fecha_iso?: string | null;
  hora?: string | null;
  descripcion?: string | null;
  estilo?: string | null;
  imagen_url?: string | null;
  source_id?: string | null;
  url_venta?: string | null;
  precio_num?: number | null;
  latitud?: number | null;
  longitud?: number | null;
  created_at?: string | null;
  updated_at?: string | null;
}

function normalizeDateTime(fechaIso?: string | null, hora?: string | null): string | null {
  if (!fechaIso) return null;
  const cleanDate = fechaIso.trim();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(cleanDate)) return cleanDate;
  if (hora && /^\d{2}:\d{2}/.test(hora)) return `${cleanDate}T${hora.slice(0, 5)}:00`;
  return `${cleanDate}T00:00:00`;
}

function tagsFromRow(row: SupabaseEventRow): string[] {
  return [row.estilo, row.lugar, row.source_id].filter((value): value is string => Boolean(value?.trim()));
}

export function mapSupabaseEvent(row: SupabaseEventRow): EventCandidate {
  return {
    id: String(row.id),
    title: row.nombre ?? null,
    description: row.descripcion ?? null,
    starts_at: normalizeDateTime(row.fecha_iso, row.hora),
    ends_at: null,
    venue_name: row.lugar ?? null,
    municipality: null,
    address: row.lugar ?? null,
    latitude: row.latitud ?? null,
    longitude: row.longitud ?? null,
    category: row.estilo ?? null,
    tags: tagsFromRow(row),
    price: row.precio_num ?? null,
    is_free: row.precio_num === 0 ? true : null,
    image_url: row.imagen_url ?? null,
    source_name: row.source_id ?? "Supabase evento",
    source_url: row.url_venta ?? null,
    created_at: row.created_at ?? null,
    updated_at: row.updated_at ?? null,
  };
}
