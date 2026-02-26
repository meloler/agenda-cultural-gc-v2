-- ==========================================
-- OPTIMIZACIÓN DE BÚSQUEDA (Full Text Search)
-- ==========================================

-- 1. Añadimos una columna oculta tipo tsvector que se actualiza automáticamente
-- Combina nombre (prioridad A), lugar/estilo (prioridad B) y descripción (prioridad C).
ALTER TABLE public.evento 
ADD COLUMN IF NOT EXISTS fts tsvector GENERATED ALWAYS AS (
  setweight(to_tsvector('spanish', coalesce(nombre, '')), 'A') ||
  setweight(to_tsvector('spanish', coalesce(lugar, '')), 'B') ||
  setweight(to_tsvector('spanish', coalesce(estilo, '')), 'B') ||
  setweight(to_tsvector('spanish', coalesce(descripcion, '')), 'C')
) STORED;

-- 2. Creamos un índice GIN para que las búsquedas sean ultrarrápidas
CREATE INDEX IF NOT EXISTS idx_evento_fts ON public.evento USING GIN (fts);

-- (Opcional) Habilitar la extensión de trigramas por si hicieran falta búsquedas parciales
CREATE EXTENSION IF NOT EXISTS pg_trgm;
