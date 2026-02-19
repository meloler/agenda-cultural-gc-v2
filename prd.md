# 1. Product Requirements Document (PRD) - Fase 1: MVP

**Nombre del Proyecto:** Agenda Cultural GC - MVP "La Verdad Única"
**Objetivo:** Ofrecer la base de datos de eventos más limpia, centralizada y fiable de Gran Canaria, eliminando el ruido y la duplicidad.

### 1.1 Alcance del MVP

* **Fuentes de Datos (Scope):**
  * *Institucionales:* Auditorio Alfredo Kraus, Teatro Pérez Galdós, LPA Cultura, Teatro Cuyás, Web del Cabildo, teldecultura.org, etc...
  * *Ticketeras:* Ticketmaster, Entrees.es, Tomaticket, NewEvent, tickety, entradas.com.
  * *Excluido:* Eventos privados en Instagram, TikTok o Apps cerradas (Fase 2).
* **Funcionalidades Usuario (Front-end):**
  * **"De un vistazo":** Dashboard minimalista con lo urgente (Hoy / Mañana / Fin de semana).
  * **Filtros Intuitivos:** Chips seleccionables (no menús desplegables complejos): "Cerca de mí", "Música", "Gratis", "Niños".
  * **Ficha de Evento:** Título, Fecha, Hora, Lugar, Precio unificado (rango) y botón "Comprar" (redirección a fuente oficial).

### 1.2 Requisitos No Funcionales

* **Deduplicación Agresiva:** El usuario NUNCA debe ver el mismo concierto dos veces.
* **Geolocalización:** Precisión de coordenadas para el filtro "Cerca de mí".
* **Velocidad:** Carga < 1s. Diseño Mobile-First.

---

# 2. Documentación Técnica y Stack Tecnológico

### 2.1 Stack Preferido (Optimizado para Python + AI Vibecoding)

* **Lenguaje Principal:** Python 3.12+ (Estándar de facto para data/scraping).
* **Framework de Scraping:** `Scrapy` (para estructura y velocidad) + `Playwright` (solo para sitios con JS pesado/bloqueos).
* **Base de Datos:** `PostgreSQL` + extensión `PostGIS` (manejo nativo de coordenadas y búsquedas por radio).
* **Backend / API:** `FastAPI` (rápido, tipado estático que ayuda a la IA a no cometer errores).
* **Frontend:** `Next.js` (React) + `Tailwind CSS` (para iteración visual rápida).
* **Orquestación:** `Prefect` o `Airflow` (para programar los scrapers).

### 2.2 Arquitectura de Datos: El "Canon"

El corazón del sistema es el algoritmo de deduplicación.

1. **Raw Layer:** Se guarda el JSON/HTML crudo de cada fuente.
2. **Normalized Layer:** Se extraen campos comunes (Título, Fecha ISO, Precio, Venue).
3. **Master Layer (Deduplication Logic):**
   * *Fuzzy Matching:* Si `Fecha` es idéntica Y `Venue` es similar (>90%) Y `Título` tiene similitud semántica (>80%) ->  **FUSIONAR** .
   * *Prioridad:* Datos Institucionales > Ticketeras > Otros.
