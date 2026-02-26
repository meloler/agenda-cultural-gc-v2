/* ================================================================
   Agenda Cultural GC — app.js v3.0
   SPA with hash routing, 4 views, PWA, share, JSON-LD
   Direct Supabase connection (no backend API needed)
   ================================================================ */

// ── Supabase config ──────────────────────────────────────────────
const SUPABASE_URL = window.ENV?.SUPABASE_URL;
const SUPABASE_ANON_KEY = window.ENV?.SUPABASE_ANON_KEY;

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  console.warn("⚠️ Advertencia: No se encontraron las credenciales de Supabase. Genera el env.js corriendo 'npm run build'.");
}

const sb = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const PAGE_SIZE = 18;
const SITE_URL = window.location.origin;

// ── State ──────────────────────────────────────────────────────────
const state = {
  view: 'grid',
  page: 1,
  total: 0,
  pages: 0,
  categoria: '',
  dateFilter: 'all',
  search: '',
  sort: 'fecha',
  debounceTimer: null,
  allEvents: null,
  calMonth: new Date().getMonth(),
  calYear: new Date().getFullYear(),
  weekOffset: 0,
  mapInstance: null,
  eventId: null,
};

// ── Category config ───────────────────────────────────────────────
const CAT_EMOJI = {
  'Música': '🎵', 'Teatro': '🎭', 'Cine': '🎬', 'Danza': '💃', 'Humor': '🤣',
  'Gastronomía': '🍽️', 'Deporte': '⚽', 'Infantil': '🎈', 'Formación': '📚',
  'Exposición': '🖼️', 'Carnaval': '🎉', 'Cultura/Teatro': '🎭', 'Otros': '🌴',
};
const CAT_COLOR = {
  'Música': '#38bdf8', 'Teatro': '#a78bfa', 'Cine': '#94a3b8', 'Danza': '#f472b6',
  'Humor': '#fbbf24', 'Gastronomía': '#f59e0b', 'Deporte': '#4ade80', 'Infantil': '#f472b6',
  'Formación': '#fbbf24', 'Exposición': '#22d3ee', 'Carnaval': '#fb7185',
  'Cultura/Teatro': '#a78bfa', 'Otros': '#94a3b8',
};

function catEmoji(cat) {
  for (const [k, v] of Object.entries(CAT_EMOJI)) {
    if (cat && cat.toLowerCase().includes(k.toLowerCase())) return v;
  }
  return '🌴';
}
function catColor(cat) {
  for (const [k, v] of Object.entries(CAT_COLOR)) {
    if (cat && cat.toLowerCase().includes(k.toLowerCase())) return v;
  }
  return '#94a3b8';
}

// ── Date helpers ──────────────────────────────────────────────────
const toISO = d => d.toISOString().slice(0, 10);
const pad = n => String(n).padStart(2, '0');

function dateRange(filter) {
  const now = new Date();
  const today = toISO(now);
  if (filter === 'today') return { fecha_inicio: today, fecha_fin: today };
  if (filter === 'tomorrow') {
    const t = new Date(now); t.setDate(t.getDate() + 1);
    return { fecha_inicio: toISO(t), fecha_fin: toISO(t) };
  }
  if (filter === 'weekend') {
    const d = new Date(now);
    const day = d.getDay();
    const toSat = (6 - day + 7) % 7 || 7;
    const sat = new Date(d); sat.setDate(d.getDate() + toSat);
    const sun = new Date(d); sun.setDate(d.getDate() + toSat + 1);
    return { fecha_inicio: toISO(sat), fecha_fin: toISO(sun) };
  }
  if (filter === 'month') {
    const y = now.getFullYear(), m = now.getMonth() + 1;
    const last = new Date(y, m, 0).getDate();
    return { fecha_inicio: today, fecha_fin: `${y}-${pad(m)}-${last}` };
  }
  return {};
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric', month: 'short' });
}
function formatDateLong(iso) {
  if (!iso) return '—';
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
}
function formatPrice(p) {
  if (p === null || p === undefined) return 'Consultar';
  if (p === 0) return 'Gratis';
  return `${p.toFixed(2).replace('.', ',')} €`;
}

// ══════════════════════════════════════════════════════════════════
// SUPABASE DATA LAYER — replaces all API calls
// ══════════════════════════════════════════════════════════════════

async function fetchEventos({ page = 1, size = PAGE_SIZE, categoria, fecha_inicio, fecha_fin, sort, search } = {}) {
  const today = toISO(new Date());
  const effectiveInicio = fecha_inicio || today;

  let query = sb
    .from('evento')
    .select('*', { count: 'exact' })
    .not('fecha_iso', 'is', null)
    .gte('fecha_iso', effectiveInicio);

  // Full Text Search applied directly in the DB
  if (search && search.trim()) {
    // Escapar comillas para evitar errores de sintaxis en websearch_to_tsquery
    const safeSearch = search.trim().replace(/'/g, "''");
    query = query.textSearch('fts', safeSearch, {
      type: 'websearch',
      config: 'spanish'
    });
  }

  if (sort === 'precio_asc') {
    query = query.order('precio_num', { ascending: true, nullsFirst: false }).order('fecha_iso', { ascending: true });
  } else if (sort === 'precio_desc') {
    query = query.order('precio_num', { ascending: false, nullsFirst: false }).order('fecha_iso', { ascending: true });
  } else {
    query = query.order('fecha_iso', { ascending: true });
  }

  if (categoria) query = query.eq('estilo', categoria);
  if (fecha_fin) query = query.lte('fecha_iso', fecha_fin);

  // Pagination
  const from = (page - 1) * size;
  const to = from + size - 1;
  query = query.range(from, to);

  const { data, error, count } = await query;
  if (error) throw error;

  return {
    items: data || [],
    total: count || 0,
    page,
    size,
    pages: Math.ceil((count || 0) / size),
  };
}

async function fetchEventoDetail(id) {
  const { data, error } = await sb
    .from('evento')
    .select('*')
    .eq('id', id)
    .single();
  if (error) throw error;
  return data;
}

async function fetchCategorias() {
  const today = toISO(new Date());
  const { data, error } = await sb
    .from('evento')
    .select('estilo')
    .not('fecha_iso', 'is', null)
    .gte('fecha_iso', today);

  if (error) throw error;

  // Group by estilo and count
  const counts = {};
  (data || []).forEach(r => {
    const cat = r.estilo || 'Otros';
    counts[cat] = (counts[cat] || 0) + 1;
  });

  return Object.entries(counts)
    .map(([nombre, total]) => ({ nombre, total }))
    .sort((a, b) => b.total - a.total);
}

async function fetchAllEvents() {
  if (state.allEvents) return state.allEvents;
  const today = toISO(new Date());

  const { data, error } = await sb
    .from('evento')
    .select('*')
    .not('fecha_iso', 'is', null)
    .gte('fecha_iso', today)
    .order('fecha_iso', { ascending: true });

  if (error) throw error;
  state.allEvents = data || [];
  return state.allEvents;
}

function buildQuery() {
  const q = { page: state.page, size: PAGE_SIZE, sort: state.sort, search: state.search };
  if (state.categoria) q.categoria = state.categoria;
  const dr = dateRange(state.dateFilter);
  if (dr.fecha_inicio) q.fecha_inicio = dr.fecha_inicio;
  if (dr.fecha_fin) q.fecha_fin = dr.fecha_fin;
  return q;
}

// ── SVG Icons ─────────────────────────────────────────────────────
const ICONS = {
  cal: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>',
  clock: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
  pin: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>',
  tag: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/><circle cx="7" cy="7" r="1" fill="currentColor"/></svg>',
  back: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>',
  share: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"/></svg>',
  whatsapp: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>',
  copy: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>',
  map: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 6v16l7-4 8 4 7-4V2l-7 4-8-4-7 4zM8 2v16M16 6v16"/></svg>',
};

// ── Badge class helper ────────────────────────────────────────────
function badgeClass(cat) {
  if (!cat) return 'badge-otros';
  const slug = cat.toLowerCase()
    .replace(/\//g, ' ').trim().split(' ')[0]
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  return `badge-${slug}`;
}

// ═══════════════════════════════════════════════════════════════════
// ROUTER — History API SPA routing
// ═══════════════════════════════════════════════════════════════════
function navigateTo(url) {
  history.pushState(null, '', url);
  router();
}

function router() {
  const path = location.pathname || '/';

  // Update nav active state
  document.querySelectorAll('.nav-link,.mobile-nav-links a').forEach(link => {
    const view = link.dataset.view;
    link.classList.toggle('active',
      (view === 'grid' && (path === '/' || path === '')) ||
      (view === 'week' && path.startsWith('/semana')) ||
      (view === 'calendar' && path.startsWith('/calendario')) ||
      (view === 'map' && path.startsWith('/mapa'))
    );
  });

  // Close mobile nav
  document.getElementById('mobile-nav-drawer')?.classList.add('hidden');
  document.getElementById('mobile-menu-btn')?.classList.remove('open');

  if (path.startsWith('/evento/')) {
    const id = parseInt(path.split('/')[2]);
    state.view = 'event';
    state.eventId = id;
    renderEventDetail(id);
  } else if (path === '/semana') {
    state.view = 'week';
    renderWeekView();
  } else if (path === '/calendario') {
    state.view = 'calendar';
    renderCalendarView();
  } else if (path === '/mapa') {
    state.view = 'map';
    renderMapView();
  } else {
    state.view = 'grid';
    renderGridView();
  }
}

// ═══════════════════════════════════════════════════════════════════
// VIEW: GRID (main listing)
// ═══════════════════════════════════════════════════════════════════
function renderGridView() {
  const main = document.getElementById('app-main');
  main.innerHTML = `
    <div class="filters-bar">
      <div class="container filters-inner">
        <div class="filter-group" id="date-filters">
          <button class="pill active" data-date="all">Todos</button>
          <button class="pill" data-date="today">Hoy</button>
          <button class="pill" data-date="tomorrow">Mañana</button>
          <button class="pill" data-date="weekend">Finde</button>
          <button class="pill" data-date="month">Este mes</button>
        </div>
        <div class="filter-divider"></div>
        <button class="mobile-filter-btn" id="mobile-filter-btn" aria-expanded="false">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="21" x2="4" y2="14"></line><line x1="4" y1="10" x2="4" y2="3"></line><line x1="12" y1="21" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="3"></line><line x1="20" y1="21" x2="20" y2="16"></line><line x1="20" y1="12" x2="20" y2="3"></line><line x1="1" y1="14" x2="7" y2="14"></line><line x1="9" y1="8" x2="15" y2="8"></line><line x1="17" y1="16" x2="23" y2="16"></line></svg>
          Filtrar categorías
        </button>
        <div class="filter-group hide-on-mobile" id="category-filters">
          <button class="cat-pill active" data-cat="">Todo</button>
        </div>
      </div>
    </div>
    <div class="container">
      <div class="stats-bar">
        <span id="stats-text">Cargando…</span>
        <select id="sort-select" aria-label="Ordenar por">
          <option value="fecha">Por fecha</option>
          <option value="precio_asc">Precio ↑</option>
          <option value="precio_desc">Precio ↓</option>
        </select>
      </div>
      <div class="events-grid" id="events-grid"></div>
      <div class="empty-state hidden" id="empty-state">
        <div class="empty-icon">🔍</div>
        <h3>No se encontraron eventos</h3>
        <p>Prueba cambiando los filtros o la búsqueda</p>
        <button class="btn-reset" onclick="resetFilters()">Restablecer filtros</button>
      </div>
      <div class="pagination" id="pagination"></div>
    </div>
  `;

  // Bind date filters
  document.querySelectorAll('#date-filters .pill').forEach(btn => {
    btn.addEventListener('click', () => setDate(btn.dataset.date, btn));
  });

  // Bind sort
  document.getElementById('sort-select').addEventListener('change', e => {
    state.sort = e.target.value;
    loadGrid();
  });

  // Mobile filter toggle
  const mobileFilterBtn = document.getElementById('mobile-filter-btn');
  const catFilters = document.getElementById('category-filters');
  if (mobileFilterBtn && catFilters) {
    mobileFilterBtn.addEventListener('click', () => {
      catFilters.classList.toggle('hide-on-mobile');
      mobileFilterBtn.classList.toggle('active');
    });
  }

  // Load categories then events
  loadCategorias();
  loadGrid();
}

function cardHTML(ev) {
  const emoji = catEmoji(ev.estilo);
  const imgHTML = ev.imagen_url
    ? `<img src="${ev.imagen_url}" alt="${ev.nombre}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=&quot;card-image-placeholder&quot;>${emoji}</div>'">`
    : `<div class="card-image-placeholder">${emoji}</div>`;

  return `
    <article class="card" data-id="${ev.id}" tabindex="0" role="button" aria-label="${ev.nombre}">
      <div class="card-image-wrap">
        ${imgHTML}
        <span class="card-badge ${badgeClass(ev.estilo)}">${ev.estilo}</span>
      </div>
      <div class="card-body">
        <h2 class="card-title">${ev.nombre}</h2>
        <div class="card-meta">
          <span>${ICONS.cal} ${formatDate(ev.fecha_iso)}</span>
          ${ev.hora ? `<span>${ICONS.clock} ${ev.hora}</span>` : ''}
        </div>
        <div class="card-footer">
          <span class="card-price${ev.precio_num === 0 ? ' free' : ''}">${formatPrice(ev.precio_num)}</span>
          <span class="card-venue">${ev.lugar}</span>
        </div>
      </div>
    </article>
  `;
}

async function loadGrid() {
  const grid = document.getElementById('events-grid');
  const emptyEl = document.getElementById('empty-state');
  const statsEl = document.getElementById('stats-text');
  if (!grid) return;

  grid.innerHTML = Array(6).fill('<div class="card skeleton"></div>').join('');
  emptyEl.classList.add('hidden');

  try {
    const q = buildQuery();
    const data = await fetchEventos(q);
    let items = data.items;

    state.total = data.total;
    state.pages = data.pages;

    statsEl.innerHTML = `<strong>${data.total}</strong> evento${data.total !== 1 ? 's' : ''} encontrado${data.total !== 1 ? 's' : ''}`;

    if (items.length === 0) {
      grid.innerHTML = '';
      emptyEl.classList.remove('hidden');
      document.getElementById('pagination').innerHTML = '';
      return;
    }

    grid.innerHTML = items.map(cardHTML).join('');
    renderPagination();

    // Card click → navigate to event detail
    grid.querySelectorAll('.card').forEach(card => {
      const go = () => navigateTo(`/evento/${card.dataset.id}`);
      card.addEventListener('click', go);
      card.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') go(); });
    });
  } catch (err) {
    console.error(err);
    grid.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:60px 0;color:var(--text-3)">
        <div style="font-size:2.5rem;margin-bottom:12px">⚠️</div>
        <p>No se pudo conectar con la base de datos.<br>Intenta recargar la página.</p>
      </div>`;
  }
}

function renderPagination() {
  const el = document.getElementById('pagination');
  if (!el || state.pages <= 1) { if (el) el.innerHTML = ''; return; }

  const MAX = 7;
  let pages = [];
  if (state.pages <= MAX) {
    pages = Array.from({ length: state.pages }, (_, i) => i + 1);
  } else {
    const s = [1];
    const around = [state.page - 1, state.page, state.page + 1].filter(p => p > 1 && p < state.pages);
    const end = [state.pages];
    const all = [...new Set([...s, ...around, ...end])].sort((a, b) => a - b);
    let prev = null;
    for (const p of all) { if (prev && p - prev > 1) pages.push('…'); pages.push(p); prev = p; }
  }

  el.innerHTML = `
    <button class="page-btn" ${state.page <= 1 ? 'disabled' : ''} onclick="goPage(${state.page - 1})">‹</button>
    ${pages.map(p => p === '…'
    ? `<span class="page-btn" style="pointer-events:none">…</span>`
    : `<button class="page-btn ${p === state.page ? 'active' : ''}" onclick="goPage(${p})">${p}</button>`
  ).join('')}
    <button class="page-btn" ${state.page >= state.pages ? 'disabled' : ''} onclick="goPage(${state.page + 1})">›</button>
  `;
}

async function loadCategorias() {
  const cats = await fetchCategorias();
  const el = document.getElementById('category-filters');
  if (!el) return;

  // "Todo" pill first
  const todoBtn = el.querySelector('[data-cat=""]');
  if (todoBtn) todoBtn.addEventListener('click', () => setCategoria('', todoBtn));

  cats.forEach(c => {
    const btn = document.createElement('button');
    btn.className = 'cat-pill';
    btn.dataset.cat = c.nombre;
    btn.innerHTML = `${catEmoji(c.nombre)} ${c.nombre} <span class="cat-count">${c.total}</span>`;
    btn.addEventListener('click', () => setCategoria(c.nombre, btn));
    el.appendChild(btn);
  });
}

function setDate(filter, btn) {
  state.dateFilter = filter;
  state.page = 1;
  document.querySelectorAll('#date-filters .pill').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  loadGrid();
}
function setCategoria(cat, btn) {
  if (state.categoria === cat && cat !== '') { state.categoria = ''; btn.classList.remove('active'); }
  else {
    state.categoria = cat;
    document.querySelectorAll('#category-filters .cat-pill').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }
  state.page = 1;
  loadGrid();
}
function goPage(p) {
  if (p < 1 || p > state.pages) return;
  state.page = p;
  loadGrid();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
function resetFilters() {
  state.categoria = ''; state.dateFilter = 'all'; state.search = ''; state.page = 1;
  const searchEl = document.getElementById('search-input');
  if (searchEl) searchEl.value = '';
  navigateTo('/');
}

// ═══════════════════════════════════════════════════════════════════
// VIEW: WEEK
// ═══════════════════════════════════════════════════════════════════
async function renderWeekView() {
  const main = document.getElementById('app-main');
  main.innerHTML = `<div class="container week-view">
    <div class="week-header">
      <h2 id="week-title">Esta semana</h2>
      <div class="week-nav">
        <button onclick="weekNav(-1)">← Anterior</button>
        <button onclick="weekNav(0)">Hoy</button>
        <button onclick="weekNav(1)">Siguiente →</button>
      </div>
    </div>
    <div id="week-content"><div class="loading-screen"><div class="loader-pulse"></div><p>Cargando…</p></div></div>
  </div>`;

  try {
    const events = await fetchAllEvents();
    renderWeekDays(events);
  } catch (err) {
    document.getElementById('week-content').innerHTML = '<p style="text-align:center;color:var(--text-3)">Error al cargar eventos</p>';
  }
}

function renderWeekDays(events) {
  const container = document.getElementById('week-content');
  const titleEl = document.getElementById('week-title');
  if (!container) return;

  const now = new Date();
  const monday = new Date(now);
  const dayOfWeek = now.getDay() || 7;
  monday.setDate(now.getDate() - dayOfWeek + 1 + (state.weekOffset * 7));
  monday.setHours(0, 0, 0, 0);

  const days = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    days.push(d);
  }

  const weekStart = formatDate(toISO(days[0]));
  const weekEnd = formatDate(toISO(days[6]));
  titleEl.textContent = state.weekOffset === 0 ? 'Esta semana' : `Semana del ${weekStart} al ${weekEnd}`;

  const todayStr = toISO(new Date());

  let html = '';
  days.forEach(day => {
    const iso = toISO(day);
    const isToday = iso === todayStr;
    const dayName = day.toLocaleDateString('es-ES', { weekday: 'long' });
    const dayDate = day.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });

    const dayEvents = events.filter(e => e.fecha_iso === iso);

    html += `
      <div class="day-column">
        <div class="day-label ${isToday ? 'today' : ''}">
          <span class="day-name">${dayName}</span>
          <span class="day-date">${dayDate}</span>
          ${dayEvents.length > 0 ? `<span class="day-count">${dayEvents.length}</span>` : ''}
        </div>
        <div class="day-events">
          ${dayEvents.length === 0
        ? '<div class="day-empty">Sin eventos programados</div>'
        : dayEvents.map(ev => `
              <div class="day-event-row" onclick="navigateTo('/evento/${ev.id}')" role="button" tabindex="0">
                <div class="day-event-time">${ev.hora || '—'}</div>
                <div class="day-event-img">
                  ${ev.imagen_url
            ? `<img src="${ev.imagen_url}" alt="" loading="lazy" onerror="this.parentElement.innerHTML='${catEmoji(ev.estilo)}'">`
            : catEmoji(ev.estilo)}
                </div>
                <div class="day-event-info">
                  <div class="day-event-name">${ev.nombre}</div>
                  <div class="day-event-venue">${ICONS.pin} ${ev.lugar}</div>
                </div>
                <span class="day-event-badge ${badgeClass(ev.estilo)}">${ev.estilo}</span>
              </div>
            `).join('')}
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

function weekNav(dir) {
  if (dir === 0) state.weekOffset = 0;
  else state.weekOffset += dir;
  fetchAllEvents().then(events => renderWeekDays(events));
}

// ═══════════════════════════════════════════════════════════════════
// VIEW: CALENDAR
// ═══════════════════════════════════════════════════════════════════
async function renderCalendarView() {
  const main = document.getElementById('app-main');
  main.innerHTML = `<div class="container calendar-view">
    <div class="calendar-header">
      <h2 id="cal-title"></h2>
      <div class="cal-nav">
        <button onclick="calNav(-1)">‹</button>
        <button onclick="calNav(0)" title="Hoy" style="font-size:.75rem">Hoy</button>
        <button onclick="calNav(1)">›</button>
      </div>
    </div>
    <div id="cal-grid-wrap"><div class="loading-screen"><div class="loader-pulse"></div></div></div>
    <div id="cal-day-detail"></div>
  </div>`;

  try {
    const events = await fetchAllEvents();
    renderCalGrid(events);
  } catch (err) {
    document.getElementById('cal-grid-wrap').innerHTML = '<p style="text-align:center;color:var(--text-3)">Error</p>';
  }
}

function renderCalGrid(events) {
  const wrap = document.getElementById('cal-grid-wrap');
  const titleEl = document.getElementById('cal-title');
  if (!wrap) return;

  const y = state.calYear, m = state.calMonth;
  const monthName = new Date(y, m, 1).toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });
  titleEl.textContent = monthName;

  const firstDay = new Date(y, m, 1);
  const lastDay = new Date(y, m + 1, 0);
  const startDay = (firstDay.getDay() + 6) % 7;

  const todayStr = toISO(new Date());

  const evMap = {};
  events.forEach(e => {
    if (!evMap[e.fecha_iso]) evMap[e.fecha_iso] = [];
    evMap[e.fecha_iso].push(e);
  });

  const dayHeaders = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
  let html = '<div class="cal-grid">';
  dayHeaders.forEach(d => { html += `<div class="cal-day-header">${d}</div>`; });

  for (let i = 0; i < startDay; i++) {
    const d = new Date(y, m, -startDay + i + 1);
    html += `<div class="cal-cell other-month"><span class="cal-date">${d.getDate()}</span></div>`;
  }

  for (let day = 1; day <= lastDay.getDate(); day++) {
    const iso = `${y}-${pad(m + 1)}-${pad(day)}`;
    const isToday = iso === todayStr;
    const dayEvs = evMap[iso] || [];

    html += `
      <div class="cal-cell ${isToday ? 'today' : ''}" onclick="showCalDay('${iso}')" role="button" tabindex="0">
        <span class="cal-date">${day}</span>
        ${dayEvs.length > 0 ? `
          <div class="cal-dots">
            ${dayEvs.slice(0, 5).map(e => `<span class="cal-dot" style="background:${catColor(e.estilo)}" title="${e.estilo}"></span>`).join('')}
          </div>
          <div class="cal-cell-events">
            ${dayEvs.slice(0, 2).map(e => `<span class="cal-event-mini">${e.nombre.slice(0, 20)}</span>`).join('')}
          </div>
          ${dayEvs.length > 2 ? `<span class="cal-event-count">+${dayEvs.length - 2} más</span>` : ''}
        ` : ''}
      </div>
    `;
  }

  const totalCells = startDay + lastDay.getDate();
  const remaining = (7 - totalCells % 7) % 7;
  for (let i = 1; i <= remaining; i++) {
    html += `<div class="cal-cell other-month"><span class="cal-date">${i}</span></div>`;
  }

  html += '</div>';
  wrap.innerHTML = html;
}

function calNav(dir) {
  if (dir === 0) {
    state.calMonth = new Date().getMonth();
    state.calYear = new Date().getFullYear();
  } else {
    state.calMonth += dir;
    if (state.calMonth > 11) { state.calMonth = 0; state.calYear++; }
    if (state.calMonth < 0) { state.calMonth = 11; state.calYear--; }
  }
  fetchAllEvents().then(events => renderCalGrid(events));
  document.getElementById('cal-day-detail').innerHTML = '';
}

async function showCalDay(iso) {
  const detail = document.getElementById('cal-day-detail');
  const events = await fetchAllEvents();
  const dayEvs = events.filter(e => e.fecha_iso === iso);
  const dateStr = formatDateLong(iso);

  if (dayEvs.length === 0) {
    detail.innerHTML = `<div class="cal-day-popup"><h3>${dateStr}</h3><p style="color:var(--text-3)">Sin eventos este día</p></div>`;
    return;
  }

  detail.innerHTML = `
    <div class="cal-day-popup">
      <h3>📅 ${dateStr} — ${dayEvs.length} evento${dayEvs.length > 1 ? 's' : ''}</h3>
      <div class="day-events">
        ${dayEvs.map(ev => `
          <div class="day-event-row" onclick="navigateTo('/evento/${ev.id}')" role="button" tabindex="0">
            <div class="day-event-time">${ev.hora || '—'}</div>
            <div class="day-event-img">
              ${ev.imagen_url
      ? `<img src="${ev.imagen_url}" alt="" loading="lazy" onerror="this.parentElement.innerHTML='${catEmoji(ev.estilo)}'">`
      : catEmoji(ev.estilo)}
            </div>
            <div class="day-event-info">
              <div class="day-event-name">${ev.nombre}</div>
              <div class="day-event-venue">${ev.lugar}</div>
            </div>
            <span class="day-event-badge ${badgeClass(ev.estilo)}">${ev.estilo}</span>
          </div>
        `).join('')}
      </div>
    </div>
  `;
  detail.scrollIntoView({ behavior: 'smooth' });
}

// Make global for onclick
window.showCalDay = showCalDay;
window.calNav = calNav;
window.weekNav = weekNav;
window.goPage = goPage;
window.resetFilters = resetFilters;
window.navigateTo = navigateTo;

// ═══════════════════════════════════════════════════════════════════
// VIEW: MAP
// ═══════════════════════════════════════════════════════════════════
async function renderMapView() {
  const main = document.getElementById('app-main');

  const legendItems = Object.entries(CAT_COLOR).map(([k, v]) =>
    `<span class="map-legend-item"><span class="map-legend-dot" style="background:${v}"></span>${k}</span>`
  ).join('');

  main.innerHTML = `<div class="container map-view">
    <div class="map-header">
      <h2>📍 Mapa de Eventos</h2>
      <div class="map-legend">${legendItems}</div>
    </div>
    <div id="map-container"></div>
  </div>`;

  // Wait for Leaflet to load
  if (typeof L === 'undefined') {
    await new Promise(resolve => {
      const check = setInterval(() => {
        if (typeof L !== 'undefined') { clearInterval(check); resolve(); }
      }, 100);
    });
  }

  try {
    const events = await fetchAllEvents();
    initMap(events);
  } catch (err) {
    document.getElementById('map-container').innerHTML = '<p style="padding:40px;text-align:center;color:var(--text-3)">Error al cargar mapa</p>';
  }
}

function initMap(events) {
  const container = document.getElementById('map-container');
  if (!container) return;

  if (state.mapInstance) { state.mapInstance.remove(); state.mapInstance = null; }

  const map = L.map('map-container').setView([28.1, -15.43], 11);
  state.mapInstance = map;

  const isDark = document.body.classList.contains('theme-dark');
  L.tileLayer(
    isDark
      ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
      : 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    { attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>', maxZoom: 19 }
  ).addTo(map);

  const geoEvents = events.filter(e => e.latitud && e.longitud);
  geoEvents.forEach(ev => {
    const color = catColor(ev.estilo);
    const icon = L.divIcon({
      className: 'custom-marker',
      html: `<div style="width:14px;height:14px;border-radius:50%;background:${color};border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,.3)"></div>`,
      iconSize: [14, 14],
      iconAnchor: [7, 7],
    });

    const marker = L.marker([ev.latitud, ev.longitud], { icon }).addTo(map);
    marker.bindPopup(`
      <div class="map-popup">
        <div class="map-popup-title">${ev.nombre}</div>
        <div class="map-popup-meta">${formatDate(ev.fecha_iso)} ${ev.hora ? '· ' + ev.hora : ''}<br>${ev.lugar}</div>
        <button class="map-popup-btn" onclick="navigateTo('/evento/${ev.id}')">Ver detalle</button>
      </div>
    `);
  });

  if (geoEvents.length > 0) {
    const bounds = L.latLngBounds(geoEvents.map(e => [e.latitud, e.longitud]));
    map.fitBounds(bounds, { padding: [30, 30] });
  }

  setTimeout(() => map.invalidateSize(), 200);
}

// ═══════════════════════════════════════════════════════════════════
// VIEW: EVENT DETAIL (shareable URL)
// ═══════════════════════════════════════════════════════════════════
async function renderEventDetail(id) {
  const main = document.getElementById('app-main');
  main.innerHTML = `<div class="container event-detail-view">
    <div class="loading-screen"><div class="loader-pulse"></div><p>Cargando evento…</p></div>
  </div>`;

  try {
    const ev = await fetchEventoDetail(id);
    const detailContainer = main.querySelector('.event-detail-view');
    const emoji = catEmoji(ev.estilo);

    const precio = formatPrice(ev.precio_num);
    const mapUrl = (ev.latitud && ev.longitud)
      ? `https://www.google.com/maps?q=${ev.latitud},${ev.longitud}`
      : null;

    const shareText = `🎭 ${ev.nombre} — ${formatDate(ev.fecha_iso)} en ${ev.lugar}`;
    const shareUrl = `${SITE_URL}/evento/${ev.id}`;
    const waUrl = `https://wa.me/?text=${encodeURIComponent(shareText + '\n' + shareUrl)}`;

    detailContainer.innerHTML = `
      <a href="/" class="event-detail-back">${ICONS.back} Volver a eventos</a>

      ${ev.imagen_url ? `
        <div class="event-detail-image">
          <img src="${ev.imagen_url}" alt="${ev.nombre}" loading="lazy"
               onerror="this.parentElement.innerHTML='<div class=&quot;card-image-placeholder&quot; style=&quot;height:240px&quot;>${emoji}</div>'">
        </div>
      ` : ''}

      <div class="event-detail-badges">
        <span class="card-badge ${badgeClass(ev.estilo)}" style="position:static">${ev.estilo}</span>
      </div>

      <h1 class="event-detail-title">${ev.nombre}</h1>

      <div class="event-info-grid">
        <div class="event-info-card">
          <div class="event-info-icon">📅</div>
          <div>
            <div class="event-info-label">Fecha</div>
            <div class="event-info-value">${formatDateLong(ev.fecha_iso)}</div>
          </div>
        </div>
        ${ev.hora ? `
        <div class="event-info-card">
          <div class="event-info-icon">🕐</div>
          <div>
            <div class="event-info-label">Hora</div>
            <div class="event-info-value">${ev.hora}</div>
          </div>
        </div>` : ''}
        <div class="event-info-card">
          <div class="event-info-icon">📍</div>
          <div>
            <div class="event-info-label">Lugar</div>
            <div class="event-info-value">${ev.lugar}</div>
          </div>
        </div>
        <div class="event-info-card">
          <div class="event-info-icon">💰</div>
          <div>
            <div class="event-info-label">Precio</div>
            <div class="event-info-value">${precio}</div>
          </div>
        </div>
      </div>

      ${ev.descripcion ? `<div class="event-detail-desc">${ev.descripcion}</div>` : ''}

      <div class="event-detail-actions">
        <a class="btn-buy" href="${ev.url_venta}" target="_blank" rel="noopener">🎟️ Comprar entradas</a>
        ${mapUrl ? `<a class="btn-secondary" href="${mapUrl}" target="_blank" rel="noopener">${ICONS.map} Ver en mapa</a>` : ''}
        <a class="btn-secondary btn-share-whatsapp" href="${waUrl}" target="_blank" rel="noopener">${ICONS.whatsapp} WhatsApp</a>
        <button class="btn-secondary" onclick="shareEvent(${ev.id},'${ev.nombre.replace(/'/g, "\\'")}')">${ICONS.share} Compartir</button>
        <button class="btn-secondary" onclick="copyLink('${shareUrl}')">${ICONS.copy} Copiar enlace</button>
      </div>
    `;

    injectEventJsonLd(ev);
    document.title = `${ev.nombre} — Agenda Cultural Gran Canaria`;

  } catch (err) {
    console.error(err);
    main.querySelector('.event-detail-view').innerHTML = `
      <a href="/" class="event-detail-back">${ICONS.back} Volver</a>
      <div class="empty-state">
        <div class="empty-icon">😕</div>
        <h3>Evento no encontrado</h3>
        <p>Es posible que el evento haya sido eliminado o que el enlace sea incorrecto.</p>
        <a href="/" class="btn-reset">Volver al inicio</a>
      </div>
    `;
  }
}

// ── JSON-LD for event (SEO) ──────────────────────────────────────
function injectEventJsonLd(ev) {
  const el = document.getElementById('event-jsonld');
  if (!el) return;

  const data = {
    "@context": "https://schema.org",
    "@type": "Event",
    "name": ev.nombre,
    "startDate": ev.fecha_iso + (ev.hora ? `T${ev.hora}:00` : ''),
    "description": ev.descripcion || `Evento de ${ev.estilo} en ${ev.lugar}, Gran Canaria`,
    "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
    "eventStatus": "https://schema.org/EventScheduled",
    "url": ev.url_venta,
    "location": {
      "@type": "Place",
      "name": ev.lugar,
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Las Palmas de Gran Canaria",
        "addressRegion": "Canarias",
        "addressCountry": "ES"
      }
    },
    "organizer": {
      "@type": "Organization",
      "name": ev.organiza
    }
  };

  if (ev.imagen_url) data.image = ev.imagen_url;
  if (ev.latitud && ev.longitud) {
    data.location.geo = {
      "@type": "GeoCoordinates",
      "latitude": ev.latitud,
      "longitude": ev.longitud
    };
  }
  if (ev.precio_num !== null && ev.precio_num !== undefined) {
    data.offers = {
      "@type": "Offer",
      "price": ev.precio_num,
      "priceCurrency": "EUR",
      "url": ev.url_venta,
      "availability": "https://schema.org/InStock"
    };
  }

  el.textContent = JSON.stringify(data);
}

// ── Share helpers ─────────────────────────────────────────────────
async function shareEvent(id, name) {
  const url = `${SITE_URL}/evento/${id}`;
  const text = `🎭 ${name} — Agenda Cultural Gran Canaria`;

  if (navigator.share) {
    try {
      await navigator.share({ title: name, text, url });
    } catch { }
  } else {
    copyLink(url);
  }
}

function copyLink(url) {
  navigator.clipboard.writeText(url).then(() => {
    showToast('✅ Enlace copiado al portapapeles');
  }).catch(() => {
    showToast('❌ No se pudo copiar el enlace');
  });
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.remove('hidden');
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.add('hidden'), 3000);
}

// Make global
window.shareEvent = shareEvent;
window.copyLink = copyLink;

// ═══════════════════════════════════════════════════════════════════
// THEME TOGGLE
// ═══════════════════════════════════════════════════════════════════
function initTheme() {
  const saved = localStorage.getItem('agcgc-theme');
  if (saved) {
    document.body.className = saved;
  } else {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.body.className = prefersDark ? 'theme-dark' : 'theme-light';
  }
}

function toggleTheme() {
  const isDark = document.body.classList.contains('theme-dark');
  document.body.className = isDark ? 'theme-light' : 'theme-dark';
  localStorage.setItem('agcgc-theme', document.body.className);

  if (state.view === 'map' && state.mapInstance) {
    state.mapInstance.remove();
    state.mapInstance = null;
    fetchAllEvents().then(events => initMap(events));
  }
}

// ═══════════════════════════════════════════════════════════════════
// PWA — Register Service Worker
// ═══════════════════════════════════════════════════════════════════
function initPWA() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(() => { });
  }
}

// ═══════════════════════════════════════════════════════════════════
// MOBILE MENU
// ═══════════════════════════════════════════════════════════════════
function initMobileMenu() {
  const btn = document.getElementById('mobile-menu-btn');
  const drawer = document.getElementById('mobile-nav-drawer');
  if (!btn || !drawer) return;

  btn.addEventListener('click', () => {
    drawer.classList.toggle('hidden');
    btn.classList.toggle('open');
  });

  drawer.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      drawer.classList.add('hidden');
      btn.classList.remove('open');
    });
  });

  const mobileSearch = document.getElementById('mobile-search-input');
  if (mobileSearch) {
    mobileSearch.addEventListener('input', e => {
      clearTimeout(state.debounceTimer);
      state.debounceTimer = setTimeout(() => {
        state.search = e.target.value;
        state.page = 1;
        if (state.view === 'grid') loadGrid();
      }, 350);
    });
  }
}

// ═══════════════════════════════════════════════════════════════════
// BOOTSTRAP
// ═══════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initPWA();
  initMobileMenu();

  document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);

  document.getElementById('search-input')?.addEventListener('input', e => {
    clearTimeout(state.debounceTimer);
    state.debounceTimer = setTimeout(() => {
      state.search = e.target.value;
      state.page = 1;
      if (state.view === 'grid') loadGrid();
    }, 350);
  });

  document.getElementById('modal-close')?.addEventListener('click', closeModal);
  document.getElementById('modal-overlay')?.addEventListener('click', e => {
    if (e.target === e.currentTarget) closeModal();
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

  window.addEventListener('popstate', router);
  document.addEventListener('click', e => {
    const a = e.target.closest('a');
    if (a && a.href && a.href.startsWith(window.location.origin)) {
      // Allow new tabs
      if (a.target === '_blank' || e.ctrlKey || e.metaKey) return;

      e.preventDefault();
      const path = a.getAttribute('href');
      navigateTo(path.startsWith('/') ? path : '/' + path);
    }
  });

  router();
});

function closeModal() {
  document.getElementById('modal-overlay')?.classList.add('hidden');
  document.body.style.overflow = '';
}
