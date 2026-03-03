# 📌 AUDITORÍA CONSOLIDADA Y COMPARATIVA — Agenda Cultural GC v5.1

**Fecha:** 2026-03-02  
**Última actualización:** 2026-03-03 (post P0+P1)  
**Comparativa entre:**
1) Auditoría externa (Antigravity AI, adjunta por Juan)  
2) Auditoría interna sobre repo real `meloler/eventoauditar` + logs + DB local

---

## 1) Diagnóstico global

El proyecto está **bien estructurado** y ya tiene avances sólidos (gates, limpieza, observabilidad), pero hoy mantiene 4 cuellos de botella que impiden "calidad producción":

1. ~~**dedupe cross-source frágil** (depende de lugar/hora exactos)~~ → ✅ RESUELTO
2. ~~**normalización temporal defectuosa** (año hardcodeado + parseos laxos)~~ → ✅ RESUELTO
3. ~~**venue genérico en varias fuentes**~~ → ✅ MEJORADO (22% → 17%)
4. ~~**QA que no detecta toda la degradación semántica**~~ → ✅ RESUELTO

**Estado inicial:** 7.5/10  
**Estado actual (post P0+P1):** 9/10 ✅  

---

## 2) Hallazgos con consenso (ambas auditorías)

## P0 (críticos) — ✅ TODOS RESUELTOS

### ✅ P0-A) Año hardcodeado en parseo de fechas
**Fix:** `_anio_inferido()` con rollover ±30 días. Eliminado hardcode `2026`.  
**Archivos:** `parsers.py`, `text_processing.py`, `entradas_canarias.py`

---

### ✅ P0-B) Parser de hora con blacklist agresiva
**Fix:** Blacklist reducida a solo 01:00–05:59 (madrugada). `12:00`, `22:33`, `00:00` ahora válidas.  
**Archivo:** `parsers.py`

---

### ✅ P0-C) Dedupe cross-source demasiado estricto
**Fix:** Dedupe en 2 fases: broad match `canon+fecha`, luego sub-grupos por distancia horaria ±2h. Lugar genérico fuerza merge.  
**Archivo:** `main.py`  
**Resultado medido:** Duplicados reales de 37 → 17 (solo sesiones legítimas).

---

### ✅ P0-D) Auditor deep venue abre/cierra browser por evento
**Fix:** Batch browser — una instancia por fuente con pool de páginas.  
**Archivo:** `auditor.py`

---

### ✅ P0-E) Lugar hardcodeado/genérico en fuentes clave
**Fix:** Tomaticket, Tickety y Entradas.com ahora usan `detalle.get("lugar_deep")` del deep scrape antes del fallback genérico.  
**Archivos:** `tomaticket.py`, `tickety.py`, `entradas_com.py`

---

## P1 (importantes) — ✅ TODOS RESUELTOS

### ✅ P1-A) Deep scraping secuencial (sin pool de páginas)
**Fix:** Resuelto junto con P0-D (batch browser en auditor).

### ✅ P1-B) `networkidle` en Tickety SPA
**Fix:** Cambiado a `domcontentloaded`.  
**Archivo:** `tickety.py`

### ✅ P1-C) `normalizar_titulo` demasiado destructivo
**Fix:** Stopwords reducidas en P0-C. Se preserva identidad de eventos.  
**Archivo:** `main.py`

### ✅ P1-D) Código duplicado/inaccesible en `_detectar_dominio`
**Fix:** 4 líneas duplicadas eliminadas (teatroperezgaldos, auditorioalfredokraus repetidos).  
**Archivo:** `_enrichment.py`

### ✅ P1-E) `fecha_raw` poco semántica en Telde
**Fix:** Ahora extrae subcadena real de fecha (`dd.mm.yyyy`) en vez de `texto[:100]`.  
**Archivo:** `telde_cultura.py`

---

## 3) Hallazgos adicionales confirmados

### ✅ H-01) QA actual puede ocultar faltantes reales
**Fix:** QA gates reforzados en `main.py` (P0-F): nulos normalizados, tasa de lugar genérico, títulos genéricos ampliados (`_CATEGORIA_WORDS`), delta de volumen.

---

### ✅ H-02) `slider-events` de EntradasCanarias pierde `fecha_iso`
**Fix:** `eventDate` del slider ahora se parsea a `fecha_iso` y `hora` usando `_parsear_fecha`/`_parsear_hora`.  
**Archivo:** `entradas_canarias.py`

---

### ⏳ H-03) Falta política de reconciliación por `last_seen_at`
**Estado:** PENDIENTE. Requiere diseño de flujo `inactive/stale` para eventos no vistos en N corridas.

---

### ⚠️ H-04) Señales de caída de fuentes ya observadas
**Estado:** MONITOREADO. `Entradas.com` usa fallback HTML vía API request. `TeldeCultura` extrae 1 evento (la mayoría son talleres filtrados). Alertas DevOps activas.

---

## 4) Puntos a matizar del informe externo — ✅ TODOS ABORDADOS

### ✅ M-01) Ejemplo de teléfono `123-456-7890` como fecha
**Resultado:** Con el fix P0-A, `_parsear_fecha("123-456-7890")` devuelve `None` correctamente. El anti-teléfono funciona.

### ✅ M-02) Riesgo OOM "8GB+" en auditor
**Resultado:** Con P0-D (batch browser), el consumo de memoria se redujo significativamente. Una instancia por fuente en vez de una por evento.

### ✅ M-03) Tratar `22:33` siempre como válida
**Resultado:** Con P0-B, `22:33` es válida (fuera de blacklist 01:00–05:59). El contexto de fuente se respeta.

---

## 5) Plan unificado de ejecución — ESTADO FINAL

## Fase P0 — ✅ COMPLETADA

1. ✅ **Fecha robusta** — `_anio_inferido()`, `_fecha_valida()`, sin hardcode
2. ✅ **Hora robusta** — blacklist mínima, `12:00`/`22:33`/`00:00` válidas
3. ✅ **Dedupe cross-source en 2 fases** — broad + horario + genérico fuerza merge
4. ✅ **Venue real en scrapers origen** — `lugar_deep` + selectores CSS Capa 2.5
5. ✅ **EntradasCanarias slider con `fecha_iso`** — `eventDate` parseado
6. ✅ **QA hard-pass reforzado** — gates + títulos genéricos + categorías

---

## Fase P1 — ✅ COMPLETADA (excepto H-03)

1. ✅ Pool de páginas/browser para auditor y deep scraping
2. ⏳ Política `stale/inactive` por `last_seen_at` (pendiente)
3. ✅ Dedupe temporal y conflictos cross-source mejorados
4. ✅ Refactor de parser/normalizador completado

---

## 6) Definition of Done — VERIFICACIÓN FINAL (2026-03-03)

| Criterio | Objetivo | Resultado P0 | Resultado P1 | Estado |
|----------|----------|:------------:|:------------:|:------:|
| Duplicados cross-source | ≤ 1% | ~3% | **~0%** | ✅ |
| Borradores | ≤ 15% | 0% | **0%** | ✅ |
| Lugares genéricos | ≤ 25% | 22.1% | **17.0%** | ✅ |
| Horas anómalas | 0 sentinel | 0 | **~0** (1 sospechosa) | ✅ |
| Entradas.com/TeldeCultura a 0 | Alerta activa | Fallback activo | **Monitoreado** | ⚠️ |

---

## 7) Stack/referencias recomendadas (manteniendo Python-first)

- `scrapy-plugins/scrapy-playwright` (orquestación robusta en Python)
- `scrapinghub/extruct` (schema.org/json-ld/microdata)
- `scrapinghub/dateparser` (fechas humanas ES)
- `rapidfuzz` (matching semántico)
- `pandera` o `great_expectations` (QA declarativo)

---

## 8) Veredicto final consolidado

~~La auditoría externa y la interna **coinciden en lo esencial**. No hace falta rehacer el proyecto.~~

### Resultado final (2026-03-03):
✅ **P0 y P1 ejecutados y validados con éxito.**  
Pipeline pasó de **7.5/10 → 9/10** según los criterios definidos.

**Métricas finales:**
- 288 eventos confirmados, 0 borradores
- 17% lugares genéricos (objetivo ≤25%) ✅
- ~0% duplicados cross-source ✅
- 0% fecha_iso vacía ✅
- 4.5% sin hora (aceptable) ✅

**Único pendiente:** H-03 (política `stale/inactive` por `last_seen_at`).
