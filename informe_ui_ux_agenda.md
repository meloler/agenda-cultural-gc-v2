# Informe Técnico de Diseño UX/UI: Agenda Cultural Gran Canaria

Este informe detalla la estructura actual del frontend (UI/UX) de la aplicación **Agenda Cultural Gran Canaria**. Está redactado para que un sistema de Inteligencia Artificial experto en rediseño web y UX/UI pueda comprender a fondo qué páginas, secciones, componentes, modales y botones interactivos componen la interfaz, facilitando la creación de una propuesta de rediseño integral.

---

## 🏗 Arquitectura General y Global
La aplicación está construida como una Single Page Application (SPA) utilizando HTML, CSS (Vanilla) y JavaScript puro, inyectando el contenido dinámicamente según la vista seleccionada.

### Opciones de Tema (Theme)
* La aplicación cuenta con modo oscuro (`theme-dark`) y claro (`theme-light`), aplicados dinámicamente sobre la etiqueta `<body>`.

### 1. Cabecera Fixa (Header / Navbar)
La cabecera `<header class="header">` siempre es visible y contiene:
1. **Logo (`.logo`)**: Un icono (🌴) con el título ("Agenda Cultural") y un subtítulo ("Gran Canaria"). Funciona como enlace al inicio.
2. **Navegación Visual (`.header-nav`)**: Selector principal de la vista actual (con iconos SVG y texto):
   * **Eventos** (`/`) - Vista de tarjetas Grid.
   * **Semana** (`/semana`) - Vista de flujo horizontal por días.
   * **Calendario** (`/calendario`) - Vista de cuadrícula mensual.
   * **Mapa** (`/mapa`) - Vista de mapa interactivo con Leaflet.
3. **Barra de Búsqueda (`.header-search`)**: Un `input` rápido con un ícono de lupa, para teclear búsquedas.
4. **Selector de Tema (`.theme-toggle`)**: Botón para cambiar entre dark/light mode con un SVG de un sol y una luna.
5. **Menú Hamburguesa (`.mobile-menu-btn`)**: Botón para pantallas pequeñas que despliega el cajón del menú.

### 2. Cajón de Navegación Móvil (`.mobile-nav-drawer`)
En dispositivos móviles, reemplaza el Header Nav. Incluye:
* Enlaces apilados en forma de lista (Eventos, Semana, Calendario, Mapa) con emojis de referencia.
* Una segunda barra de búsqueda dedicada.

### 3. Contenedor Principal (`main#app-main`)
Aquí se inyectan dinámicamente las estructuras HTML de cada una de las 4 vistas posibles (Grid, Semana, Calendario, Mapa) o la vista detallada de un evento compartido por enlace.

### 4. Pie de Página (Footer)
Componente clásico con:
* Branding y claim (eslogan).
* Enlaces rápidos (RSS, Inicio, Mapa, Calendario).
* Nota de Copyright.

### 5. Sistema Global de Overlays
* **Modal Overlay (`.modal-overlay`)**: Ocupa toda la pantalla, con un fondo semi-transparente oscurecido. Contiene un botón de cierre "✕". En el interior, inyecta el contenido detallado del evento.
* **Toasts (`.toast`)**: Pequeñas notificaciones flotantes temporales de sistema (ej. "Enlace copiado").
* **Vista de Carga (`.loading-screen`)**: Contenedor central con un spinner (`.loader-pulse`) y texto ("Cargando…").
* **Estado Vacío (`.empty-state`)**: Se muestra cuando no hay nada que ver (ej. búsqueda sin resultados). Incluye un ícono 🔍, texto de aviso, y un botón "Restablecer filtros" (`.btn-reset`).

---

## 🗂 Vista 1: Grid (Página Inicial / Todos los eventos)
Esta es la pantalla principal para explorar y descubrir eventos libremente.

### 1.1 Barra de Filtros (`.filters-bar`)
Es una franja bajo el header con dos secciones, separadas por un divisor visual:
* **Filtros de Fecha (`#date-filters`)**: Botones en formato "píldora" (`.pill`): *Todos, Hoy, Mañana, Finde, Este mes*.
* **Filtros de Categoría (`#category-filters`)**: Botones dinámicos tipo píldora (`.cat-pill`) con colores asociados a su categoría (ej. verde para Deportes, morado para Teatro). Un botón inicial es "Todo".
* **Botón móvil ("Filtrar categorías")**: En móviles, por falta de espacio, se condensa el grupo de categorías tras un botón desplegable.

### 1.2 Barra de Estadísticas y Ordenamiento (`.stats-bar`)
Situada justo encima de los resultados:
* Texto a la izquierda: "XX eventos encontrados".
* `select` a la derecha: Dropdown nativo para ordenar por (Fecha, Precio ↑, Precio ↓).

### 1.3 Rejilla de Tarjetas (`.events-grid`)
Contenedor modular grid (CSS grid) para listar los eventos y paginación.

### Componente: Tarjeta de Evento (Event Card `.card`)
Las tarjetas responden a la interacción (hover, tabindex). Contienen:
* **Bloque Superior (`.card-image-wrap`)**:
  * Imagen a sangría completa, o un "placeholder" de color con un emoji grande en el centro si falta la foto.
  * Etiqueta / Badge (`.card-badge`): Flotando en una esquina del thumbnail de imagen indicando la categoría, con un fondo semi-transparente del color de la categoría.
* **Bloque Inferior (Cuerpo - `.card-body`)**:
  * Título truncable (`.card-title`).
  * Metadatos visuales (`.card-meta`): Dos filas con pequeños SVG. Fila 1: Icono de Calendario + Fecha (ej. "15 may 2026"). Fila 2: Icono Reloj + Hora (si existe).
* **Bloque Pie (Pie - `.card-footer`)**:
  * Precio en negrita a la izquierda. Si es gratis o coste 0, tiene la clase `.free`.
  * Ubicación truncable (`.card-venue`) a la derecha, con un color atenuado.

---

## 📅 Vista 2: Esta Semana (`/semana`)
Vista diseñada para ver rápidamente lo que deparan los próximos 7 días, similar al Google Calendar formato agenda.

* **Cabecera de Semana**: Título ("Esta semana" o "Semana del X al Y") y controles de paginación de semana (Atrás, Hoy, Siguiente).
* **Contenido (Columnas)**: Se renderizan hasta 7 divisores o bloques (`.day-column`).
  * **Etiqueta del Día (`.day-label`)**: Cabecera de la columna con el nombre (ej. Lunes), fecha corta (14 may), y una pequeña píldora numérica con la cantidad total de eventos en el día (`.day-count`). Si es hoy, recibe estilos resaltados (`.today`).
  * **Eventos del Día**: Listado apilado verticalmente de mini-cards (`.day-event-row`), en un estilo condensado tipo fila.
* **Componente Fila de Evento (Mini-Card)**:
  * Texto de hora a la izquierda (ej. "20:00").
  * Mini miniatura / thumbnail circular o cuadrado (`.day-event-img`).
  * Bloque central de texto: Título del evento arriba (`.day-event-name`) y ubicación con icono debajo (`.day-event-venue`).
  * Badge de Categoría apaisado a la derecha.

---

## 🗓 Vista 3: Calendario (`/calendario`)
Vista tradicional de grilla mensual clásica.

* **Cabecera**: Contenedor muy similar al de semana, con el Nombre del Mes y Año como título principal. Controles (Mes Anterior, Hoy, Mes Siguiente).
* **Contenedor Principal (`.cal-grid`)**:
  * Cabeceras estructurales de días: (Lun, Mar, Mié...).
  * Celdas funcionales (`.cal-cell`). Tienen bordes.
* **Comportamiento Celda de Calendario (`.cal-cell`)**:
  * Un número arriba a la izquierda (`.cal-date`).
  * **Puntos de Color (`.cal-dots`)**: Una fila de circulitos minúsculos coloreados que se sitúan abajo de la fecha (se muestran hasta 5 colores según categorías), para vistazo ultrarrápido sin clics.
  * **Textos Mini (`.cal-cell-events`)**: Nombres ultra-recortados (max 20 caracteres) de los 2 primeros eventos del día.
  * **Contador Sobrante (`.cal-event-count`)**: El clásico "+X más" si rebasan los 2 eventos mostrados.

---

## 📍 Vista 4: Mapa (`/mapa`)
Vista exploratoria geoespacial usando el motor Leaflet.

* **Cabecera de Mapa**: Título principal "📍 Mapa de Eventos" a un lado. Al otro lado, una leyenda visual (`.map-legend`) renderizada como un flex row de puntos de colores y los nombres de categoría al lado para saber "qué color representa a qué" (`<span class="map-legend-dot"></span> Categoría`).
* **Contenedor de Lienzo (`#map-container`)**: Ocupa el espacio base donde se incrusta el iframe renderizado de mapas nativos. Los pines (`Markers`) dentro del mapa tienen que ir alineados con la leyenda.

---

## 🎟️ Detalle Completo de un Evento (Modal Popup / URL Independiente)
Representa la ficha final del evento (`.event-detail-view` o `.modal-content`), donde el usuario consulta si quiere asistir.

1. **Botón superior**: Enlace "Volver a eventos" a la izquierda.
2. **Imagen Cabecera (`.event-detail-image`)**: Una fotografía extendida tipo portada superior de héroe. Si falla o falta, se vuelve un placeholder de aspecto 16:9 con un emoji gigante de la categoría flotando.
3. **Píldora del Estilo (`.event-detail-badges`)**: La categoría marcada arriba, estática (sin flotar).
4. **Título Principal (`.h1.event-detail-title`)**: Tamaño de fuente muy grande que define la vista.
5. **Rejilla de Información (`.event-info-grid`)**: Disposición habitualmente de 2x2. Consta de 4 tarjetas o "boxes" internas (`.event-info-card`), cada una con un gran emoji-ícono representativo, seguido de una etiqueta (Label) "Fecha", "Hora", "Lugar", "Precio", y debajo el valor en sí.
6. **Bloque de Descripción (`.event-detail-desc`)**: Ámbito libre para párrafos con sinopsis, HTML parseado.
7. **Barra Fija Inferior/Panel de Acción (`.event-detail-actions`)**:
   * **Super-Botón Primario (`.btn-buy`)**: "🎟️ Comprar entradas", suele ser resaltado sobre los demás visualmente.
   * Botón Secundario - Mapa (`.btn-secondary`): "Ver en mapa".
   * Botones Sociales (`.btn-secondary`): WhatsApp, Compartir Nativo móvil y Copiar Enlace. Se colocan alineados en una cuadrícula o grid apilable.

---

## 💡 Recomendaciones para la IA de UX/UI
* **Estética de Ocio:** Al tratarse de una Agenda Cultural insular, propón una paleta vibrante sobre un fondo neutral (blanco/glass oscuro) que inspire "planes sociales y diversión", huyendo de interfaces aburridas ("dashboards puros").
* **Uso de Glassmorphism & Micro-interacciones:** La transición de las tabs de la cabecera (Grid, Map, Calendar, Week) podrían ser botones de tipo "segment toggle".
* **Imágenes de Eventos inconsistentes:** Dado que las imágenes proceden de scrapping heterogéneo (distintos carteles verticales y horizontales), el layout debe contemplar proporciones universales, cortes dinámicos (`object-fit: cover`) o viñetas difuminadas por debajo.
* **Espacio Crítico Móvil (`Mobile First`):** Reemplazar los text-links que existen por bottom-sheet modales reales; el rediseño debería contemplar un rediseño radical de la tarjeta-fila de "Esta Semana" para aprovechar los límites de la pantalla del smartphone.
* **Componentización de las Box (`.event-info-card`):** Actualmente el detalle del evento carga cuadritos de información. En el rediseño se debería pensar en layouts fluidos, iconos de sistema (no emojis) e iteración visual profunda.
