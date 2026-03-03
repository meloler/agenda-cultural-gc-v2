# 📌 AUDITORÍA CONSOLIDADA Y COMPARATIVA — Agenda Cultural GC v5.1

**Fecha:** 2026-03-02  
**Comparativa entre:**
1) Auditoría externa (Antigravity AI, adjunta por Juan)  
2) Auditoría interna sobre repo real `meloler/eventoauditar` + logs + DB local

---

## 1) Diagnóstico global

El proyecto está **bien estructurado** y ya tiene avances sólidos (gates, limpieza, observabilidad), pero hoy mantiene 4 cuellos de botella que impiden “calidad producción”:

1. **dedupe cross-source frágil** (depende de lugar/hora exactos),
2. **normalización temporal defectuosa** (año hardcodeado + parseos laxos),
3. **venue genérico en varias fuentes**,
4. **QA que no detecta toda la degradación semántica**.

**Estado actual estimado:** 7.5/10  
**Objetivo con P0+P1 cerrados:** 9/10

---

## 2) Hallazgos con consenso (ambas auditorías)

## P0 (críticos)

### P0-A) Año hardcodeado en parseo de fechas (`2026`)
**Archivos:**
- `scrapers/app/utils/parsers.py`
- `scrapers/app/utils/text_processing.py`
- `scrapers/app/scrapers/entradas_canarias.py`

**Efecto:** fechas incorrectas en transición anual / fallback engañoso.

---

### P0-B) Parser de hora con blacklist agresiva
**Archivo:** `scrapers/app/utils/parsers.py`

Se eliminan horas potencialmente válidas (`12:00`, etc.), lo que sube falsamente “hora por confirmar”.

---

### P0-C) Dedupe cross-source demasiado estricto
**Archivo:** `scrapers/main.py`

Clave actual incluye `hora` + `lugar_norm`; si dos fuentes difieren ligeramente, **no fusiona**.

---

### P0-D) Auditor deep venue abre/cierra browser por evento
**Archivo:** `scrapers/app/auditor.py`

Coste alto de latencia y estabilidad.

---

### P0-E) Lugar hardcodeado/genérico en fuentes clave
**Archivos:**
- `scrapers/app/scrapers/tomaticket.py` (`Gran Canaria`)
- `scrapers/app/scrapers/tickety.py` (`Gran Canaria`)
- `scrapers/app/scrapers/entradas_com.py` (`Las Palmas de Gran Canaria`)

Rompe dedupe y geocodificación fina.

---

## P1 (importantes)

### P1-A) Deep scraping secuencial (sin pool de páginas)
Cuello de botella claro de tiempo.

### P1-B) `networkidle` en Tickety SPA
**Archivo:** `scrapers/app/scrapers/tickety.py`  
Conviene `domcontentloaded` + wait explícito por selector.

### P1-C) `normalizar_titulo` demasiado destructivo
**Archivo:** `scrapers/main.py`  
Stopwords tipo `tour/gira/concierto` pueden borrar identidad útil.

### P1-D) Código duplicado/inaccesible en `_detectar_dominio`
**Archivo:** `scrapers/app/scrapers/_enrichment.py`

### P1-E) `fecha_raw` poco semántica en Telde
**Archivo:** `scrapers/app/scrapers/telde_cultura.py`  
Se guarda fragmento de texto largo, no “fecha cruda” real.

---

## 3) Hallazgos adicionales confirmados (aparecen en la auditoría interna y complementan)

### H-01) QA actual puede ocultar faltantes reales
**Archivo:** `scrapers/scripts/qa_report.py`

Chequea vacíos por literales (`"Hora por confirmar"`, `"Consultar"`) y no por normalización robusta de nulos.  
Además, dedupe QA por `Evento+Fecha` exacto no detecta duplicado semántico.

---

### H-02) `slider-events` de EntradasCanarias pierde `fecha_iso`
**Archivo:** `scrapers/app/scrapers/entradas_canarias.py`

`eventDate` se conserva en raw pero no se normaliza a ISO en esa rama.

---

### H-03) Falta política de reconciliación por `last_seen_at`
Hay marca de “seen”, pero no flujo claro de `inactive/stale` por no aparición en N corridas.

---

### H-04) Señales de caída de fuentes ya observadas
En logs recientes: `Entradas.com` y `TeldeCultura` con extracción 0 en corrida concreta.

---

## 4) Puntos a matizar del informe externo (importante para no sobrecorregir)

### M-01) Ejemplo de teléfono `123-456-7890` como fecha
El caso concreto está **sobredimensionado**: con regex actual no entra tal cual por límites de grupos `\d{1,2}`.  
Sí existe problema de ambigüedad `DD/MM`, pero ese ejemplo exacto no es el mejor.

### M-02) Riesgo OOM “8GB+” en auditor
La implementación actual es ineficiente, sí; pero al ser secuencial y cerrando browser, el OOM masivo no siempre se materializa así de lineal. El riesgo principal hoy es **latencia + inestabilidad**.

### M-03) Tratar `22:33` siempre como válida
Hay que matizar: puede ser válida en casos puntuales, pero en este pipeline aparece como valor “sospechoso” recurrente. Mejor **no hard-drop universal** ni hard-allow universal: usar score de fiabilidad por contexto/fuente.

---

## 5) Plan unificado de ejecución (prioridad real)

## Fase P0 (impacto máximo, 1 día)

1. **Fecha robusta**
   - quitar hardcode de año,
   - validación estricta de rango,
   - inferencia de año por rollover controlado.

2. **Hora robusta**
   - reducir blacklist agresiva,
   - filtrar anómalas por contexto/fuente, no por lista rígida.

3. **Dedupe cross-source en 2 fases**
   - fase broad: `canon + fecha`,
   - fase resolve: separar sesiones por distancia horaria + venue + source confidence.

4. **Venue real en scrapers origen**
   - Tomaticket/Tickety/Entradas.com deben intentar venue específico antes de fallback genérico.

5. **EntradasCanarias slider con `fecha_iso`**
   - parsear `eventDate` igual que sessions API.

6. **QA hard-pass reforzado**
   - nulos normalizados reales,
   - tasa de lugar genérico,
   - detección de clusters repetitivos,
   - delta de volumen vs corrida previa.

---

## Fase P1 (2–3 días)

1. pool de páginas/browser para auditor y deep scraping,  
2. política `stale/inactive` por `last_seen_at`,  
3. tests E2E de dedupe temporal y conflictos cross-source,  
4. refactor de parser/normalizador para bajar heurística regex indiscriminada.

---

## 6) Definition of Done (criterios para declarar “arreglado”)

- **Duplicados cross-source visibles** <= 1% (métrica semántica, no exact-match).
- **Borradores** <= 15% sostenido en 3 corridas.
- **Lugares genéricos** <= 25% (y decreciendo por fuente).
- **Horas sentinel/anómalas** 0 en confirmados (o justificadas por regla de fuente).
- **Entradas.com/TeldeCultura**: no más corridas consecutivas a 0 sin alerta bloqueante.

---

## 7) Stack/referencias recomendadas (manteniendo Python-first)

- `scrapy-plugins/scrapy-playwright` (orquestación robusta en Python)
- `scrapinghub/extruct` (schema.org/json-ld/microdata)
- `scrapinghub/dateparser` (fechas humanas ES)
- `rapidfuzz` (matching semántico)
- `pandera` o `great_expectations` (QA declarativo)
- `pinchtab` (solo para escalar infraestructura de browser, no para calidad de datos)

---

## 8) Veredicto final consolidado

La auditoría externa y la interna **coinciden en lo esencial**.  
No hace falta rehacer el proyecto: con un refactor quirúrgico en **fecha/hora + venue + dedupe + QA**, el pipeline puede pasar a un nivel de calidad alto y estable.

**Recomendación final:** ejecutar P0 ya, medir 2 corridas, luego cerrar P1.
