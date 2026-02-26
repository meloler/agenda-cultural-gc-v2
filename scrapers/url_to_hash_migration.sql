-- ==========================================
-- ACTUALIZACIÓN DE PK Y UNIQUE CONSTRAINT (url_venta -> hash_id)
-- ==========================================

-- 1. Si los registros actuales no tienen un hash_id, necesitamos generarlo usando crypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2. Asegurarnos de que la columna hash_id exista (los modelos de python la requieren ahora)
ALTER TABLE public.evento 
ADD COLUMN IF NOT EXISTS hash_id text;

-- 3. Rellenar los hash_id existentes con un MD5 o SHA256 simulado basado en el patrón propuesto:
-- raw_id = organiza | url_venta | fecha_iso | hora
UPDATE public.evento
SET hash_id = encode(digest(
  coalesce(organiza, 'Desconocido') || '|' || 
  coalesce(url_venta, '') || '|' || 
  coalesce(fecha_iso, 'None') || '|' || 
  coalesce(hora, 'None'), 
  'sha256'
), 'hex')
WHERE hash_id IS NULL;

-- 4. Eliminar el viejo Constraint que forzaba a que url_venta fuera única
DO $$
DECLARE constraint_name text;
BEGIN
    SELECT conname INTO constraint_name
    FROM pg_constraint
    WHERE conrelid = 'public.evento'::regclass AND contype = 'u' 
    AND conname LIKE '%url_venta%';

    IF constraint_name IS NOT NULL THEN
        EXECUTE 'ALTER TABLE public.evento DROP CONSTRAINT ' || constraint_name;
    END IF;
END $$;

-- 5. Eliminar el viejo index si existiera
DROP INDEX IF EXISTS ix_evento_url_venta;

-- 6. Crear el nuevo constraint de unicidad estricta para el hash
ALTER TABLE public.evento 
ADD CONSTRAINT ix_evento_hash_id_unique UNIQUE (hash_id);

-- 7. Crear índice rápido para búsquedas e inserts
CREATE INDEX IF NOT EXISTS ix_evento_hash_id ON public.evento (hash_id);
