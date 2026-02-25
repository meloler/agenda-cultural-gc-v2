-- Habilitar RLS en la tabla principal de eventos
ALTER TABLE public.evento ENABLE ROW LEVEL SECURITY;

-- 1. Política de LECTURA PÚBLICA (Anon / Frontend)
-- Solo permite hacer SELECT a los usuarios anónimos.
-- Filtro adicional: Solo devuelve filas que NO sean borradores (fecha_iso no es nula).
CREATE POLICY "Lectura pública de eventos confirmados (Anon)" 
ON public.evento
FOR SELECT 
TO anon 
USING (fecha_iso IS NOT NULL);

-- 2. Política de ESCRITURA TOTAL (Service Role / Backend)
-- Permite todas las operaciones (INSERT, UPDATE, DELETE, SELECT) 
-- pero ÚNICAMENTE al rol autenticado como 'service_role'.
CREATE POLICY "Control total para Backend (Service Role)" 
ON public.evento
FOR ALL 
TO service_role 
USING (true)
WITH CHECK (true);

-- (Opcional) Si en el futuro tienes usuarios logueados que leen (ej. administradores que revisan borradores), 
-- también se les podría dar permisos a authenticated. Por ahora, el workflow parece ser 
-- solo Anon (Lectura Frontend) y Service Role (Escritura Scrapers).
