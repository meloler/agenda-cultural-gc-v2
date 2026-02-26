-- ==========================================
-- ACTUALIZACIÓN DE MODELO: CONSERVACIÓN DEL HISTÓRICO
-- Añadir estado a los eventos
-- ==========================================

-- 1. Añadimos la columna 'estado' con valor por defecto 'upcoming'.
ALTER TABLE public.evento 
ADD COLUMN IF NOT EXISTS estado text DEFAULT 'upcoming';

-- 2. Creamos un índice para búsquedas rápidas (muy útil para purgar o filtrar backend)
CREATE INDEX IF NOT EXISTS ix_evento_estado ON public.evento (estado);

-- 3. (Opcional pero recomendable) Si hay eventos en la BD que tienen fecha menor a hoy,
-- forzamos su actualización a 'past' para alinear los datos actuales.
UPDATE public.evento
SET estado = 'past'
WHERE fecha_iso < CURRENT_DATE::text;
