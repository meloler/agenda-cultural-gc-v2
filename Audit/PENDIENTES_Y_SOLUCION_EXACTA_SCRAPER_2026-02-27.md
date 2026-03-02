# Informe de Cierre Pendiente — Scraper (post-fixes)

 
## 1) Evidencia objetiva del estado actual

### 1.1 KPIs actuales vs objetivo

| Métrica | Actual | Objetivo | Estado |
|---|---:|---:|---|
| Eventos totales | 412 | - | ✅ |
| Títulos genéricos exactos | 0 | 0 | ✅ |
| Hora vacía | 33 (8.0%) | <= 7% | ❌ |
| Precio vacío | 32 (7.8%) | <= 12% | ✅ |
| Duplicados `canonical+fecha` | 15 grupos | 0 self-source / mínimo cross-source | ⚠️ |
| Títulos sospechosos | 9 | 0 | ❌ |
| Lugares contaminados (texto narrativo) | 8 | 0 | ❌ |
| Tokens `NaN` en JSON exportado | 32 | 0 (JSON estricto) | ❌ |
| Eventos en pasado (<2026-02-27) | 110 (26.7%) | depende política | ⚠️ |
| Descripciones con `[Generado por IA]` | 65 (15.8%) | depende política | ⚠️ |

### 1.2 Faltan horas (33 filas exactas)

Distribución por fuente:
- **CICCA: 3**
- **Tomaticket: 17**
- **EntradasCanarias: 13**

| Row | Fuente | Fecha | Evento | URL |
|---:|---|---|---|---|
| 72 | CICCA | 2026-01-23 | Cuando el cuerpo femenino se convierte en objeto: la mirada crítica de Gara Acosta en el C | https://www.fundacionlacajadecanarias.es/cuando-el-cuerpo-femenino-se-convierte-en-objeto-la-mirada-critica-de-gara-acosta-en-el-cicca/ |
| 88 | Tomaticket | 2026-02-10 | Ballet of Lights - La Bella Durmiente en Gran Canaria | https://www.tomaticket.es/es-es/entradas-ballet-of-lights-la-bella-durmiente-en-gran-canaria |
| 89 | Tomaticket | 2026-02-14 | Muerte por IA - The Jury Experience en Gran Canaria | https://www.tomaticket.es/es-es/entradas-the-jury-experience-gran-canaria |
| 93 | Tomaticket | 2026-02-18 | Aqualand Maspalomas en Gran Canaria | https://www.tomaticket.es/es-es/entradas-aqualand-gran-canaria |
| 96 | Tomaticket | 2026-02-23 | Excursiones de 1 día en Gran Canaria | https://www.tomaticket.es/es-es/entradas-excursiones-de-1-dia-en-gran-canaria |
| 97 | Tomaticket | 2026-02-23 | Bus Turístico CitySightseeing Las Palmas de Gran Canaria | https://www.tomaticket.es/es-es/entradas-citysightseeing-las-palmas-de-gran-canaria |
| 102 | Tomaticket | 2026-02-23 | Acuario Poema del Mar Gran Canaria | https://www.tomaticket.es/es-es/entradas-acuario-poema-del-mar-gran-canaria |
| 111 | EntradasCanarias | 2026-02-26 | Los fantasmas de Shakespeare | https://ventas.entradascanarias.com/events/los-fantasmas-de-shakespeare-a75e0f19-f06d-496c-a136-32f65e505528 |
| 113 | Tomaticket | 2026-02-27 | Marc Anthony en el Carnaval de Gran Canaria | https://www.tomaticket.es/es-es/entradas-marc-anthony-gran-canaria |
| 114 | EntradasCanarias | 2026-02-27 | Paula Ojeda | https://ventas.entradascanarias.com/events/paula-ojeda |
| 122 | Tomaticket | 2026-02-27 | Ballet of Lights - La Bella Durmiente en Gran Canaria | https://www.tomaticket.es/es-es/entradas-ballet-of-lights-la-bella-durmiente-en-gran-canaria |
| 129 | Tomaticket | 2026-02-28 | Ozuna en el Carnaval de Gran Canaria | https://www.tomaticket.es/es-es/entradas-ozuna-gran-canaria |
| 144 | Tomaticket | 2026-03-06 | SUPERSAURIO, EL MUSICAL de Meryem El Mehdati en Gran Canaria | https://www.tomaticket.es/es-es/entradas-supersaurio-el-musical-en-gran-canaria |
| 147 | Tomaticket | 2026-03-06 | Carlitos Brownie Band Palmas, Las | https://www.tomaticket.es/es-es/entradas-carlitos-brownie-band-palmas-las |
| 166 | EntradasCanarias | 2026-03-07 | SELVATICA "CARNIVAL EDITION" | https://venta.entradascanarias.com/entradascanarias/es_ES/entradas/evento/52317 |
| 172 | EntradasCanarias | 2026-03-08 | Liga Endesa y BCL 25/26 | https://venta.entradascanarias.com/entradascanarias/es_ES/entradas/evento/47689 |
| 177 | Tomaticket | 2026-03-11 | TALLER DE “CONCIENCIACIÓN SOBRE LA PÉRDIDA Y EL DESPERDICIO DE ALIMENTOS” Segunda edición  | https://www.tomaticket.es/es-es/entradas-taller-de-concienciacion-sobre-la-perdida-y-el-desperdicio-de-alimentos-segunda-edicion-2026-pollogallina-palmas-las |
| 184 | EntradasCanarias | 2026-03-12 | Carles Sans De Tricicle - Por Fin Me Voy | https://venta.entradascanarias.com/entradascanarias/es_ES/entradas/evento/52075 |
| 193 | Tomaticket | 2026-03-13 | LA PATÉTICA de Miguel del Arco en Gran Canaria | https://www.tomaticket.es/es-es/entradas-la-patetica-en-gran-canaria |
| 209 | EntradasCanarias | 2026-03-14 | The Class Carnival | https://venta.entradascanarias.com/entradascanarias/es_ES/entradas/evento/52086 |
| 215 | EntradasCanarias | 2026-03-15 | Saúl Romero - Estreno del nuevo show FANTASÍA | https://venta.entradascanarias.com/entradascanarias/es_ES/entradas/evento/51790 |
| 236 | EntradasCanarias | 2026-03-21 | CAMPEONATO CANARIAS MMA - THE BATTLE CHAMPIONSHIP | https://venta.entradascanarias.com/entradascanarias/es_ES/entradas/evento/51150 |
| 240 | EntradasCanarias | 2026-03-21 | CARROZA MASPALOMAS EL MONO PRODUCCIONES | https://venta.entradascanarias.com/entradascanarias/es_ES/entradas/evento/52316 |
| 249 | Tomaticket | 2026-03-26 | GRANCA Live Fest 2026 | https://www.tomaticket.es/es-es/entradas-granca-live-fest-en-gran-canaria |
| 250 | Tomaticket | 2026-03-26 | Dinosaurios Live en Gran Canaria | https://www.tomaticket.es/es-es/entradas-mundo-dinosaurios-gran-canaria |
| 317 | EntradasCanarias | 2026-05-02 | Concierto Lia Kali | https://venta.entradascanarias.com/entradascanarias/es_ES/entradas/evento/52189 |
| 361 | EntradasCanarias | 2026-06-13 | Ignorancia Artificial | https://venta.entradascanarias.com/entradascanarias/es_ES/entradas/evento/51738 |
| 369 | Tomaticket | 2026-06-20 | Luck Ra y Valentino Merlo en Gran Canaria | https://www.tomaticket.es/es-es/entradas-luck-ra-gran-canaria |
| 371 | EntradasCanarias | 2026-06-20 | Back to Rock | https://venta.entradascanarias.com/entradascanarias/es_ES/entradas/evento/51576 |
| 387 | Tomaticket | 2026-07-11 | Festival "Somos Latinos" en Las Palmas de Gran Canaria | https://www.tomaticket.es/es-es/entradas-festival-somos-latinos-en-gran-canaria |
| 394 | EntradasCanarias | 2026-07-31 | UB40 – 2026 EUROPEAN TOUR - Gran Canaria | https://venta.entradascanarias.com/entradascanarias/es_ES/entradas/evento/52993 |
| 405 | CICCA | 2026-11-05 | El CICCA abre sus puertas al talento emergente de Canarias | https://www.fundacionlacajadecanarias.es/el-cicca-abre-sus-puertas-al-talento-emergente-de-canarias/ |
| 411 | CICCA | 2026-12-18 | EL CICCA CELEBRA LOS 20 AÑOS DE HISTORIA DEL BELÉN DE ARENA | https://www.fundacionlacajadecanarias.es/el-cicca-celebra-los-20-anos-de-historia-del-belen-de-arena/ |

### 1.3 Duplicados residuales (`canonical + fecha`)

- Grupos totales: **15**
- **Misma fuente (error claro): 3**
- Multi-fuente (requieren consolidación cross-source): **12**

#### 1.3.1 Duplicados misma fuente (deben eliminarse sí o sí)
- `saul romero estreno del nuevo show fantasia` | fecha `2026-03-15` | fuentes `{'EntradasCanarias': 2}`
  - row 215 | Saúl Romero - Estreno del nuevo show FANTASÍA | hora=None | https://venta.entradascanarias.com/entradascanarias/es_ES/entradas/evento/51790
  - row 217 | Saul Romero - Estreno del nuevo Show FANTASÍA | hora=19:00 | https://entradascanarias.com/evento/entradas-saul-romero-estreno-del-nuevo-show-fantasia-las-palmas-de-gran-canaria
- `kany garcia` | fecha `2026-06-26` | fuentes `{'Entrées.es': 2}`
  - row 373 | Kany García en Las Palmas de Gran Canaria | hora=19:00 | https://entrees.es/evento/ext/kany-garcia-en-las-palmas-de-gran-canaria-entradas
  - row 374 | Kany García en LAS PALMAS DE GRAN CANARIA | hora=00:00 | https://entrees.es/evento/ext/kany-garcia-en-las-palmas-de-gran-canaria--entradas
- `sum festival 2026` | fecha `2026-10-02` | fuentes `{'Entrées.es': 2}`
  - row 399 | Gran Canaria SUM Festival 2026 | hora=22:33 | https://entrees.es/evento/ext/gran-canaria-sum-festival-2026--entradas
  - row 400 | Gran Canaria SUM Festival 2026 | hora=00:00 | https://entrees.es/evento/ext/gran-canaria-sum-festival-2026-entradas

#### 1.3.2 Duplicados multi-fuente (consolidación pendiente)
- `la reina del flow` | fecha `2026-07-10` | count=3 | sources={'Ticketmaster': 1, 'Entrées.es': 1, 'Tomaticket': 1}
  - row 383 | Ticketmaster | hora=21:00 | lugar=Auditorio San Juan de Telde | https://www.ticketmaster.es/event/la-reina-del-flow-tickets/761001134?language=en-us
  - row 384 | Entrées.es | hora=22:33 | lugar=Auditorio Parque San Juan | https://entrees.es/evento/ext/la-reina-del-flow-en-gran-canaria-entradas
  - row 385 | Tomaticket | hora=21:00 | lugar=Auditorio San Juan de Telde | https://www.tomaticket.es/es-es/entradas-la-reina-del-flow-en-gran-canaria
- `paula ojeda` | fecha `2026-02-27` | count=2 | sources={'EntradasCanarias': 1, 'Tickety': 1}
  - row 114 | EntradasCanarias | hora=None | lugar=Sótano Analógico | https://ventas.entradascanarias.com/events/paula-ojeda
  - row 115 | Tickety | hora=20:00 | lugar=Sótano Analógico | https://tickety.es/event/paula-ojeda
- `aula de cine los angeles del pecado` | fecha `2026-02-27` | count=2 | sources={'Tomaticket': 1, 'EntradasCanarias': 1}
  - row 120 | Tomaticket | hora=19:00 | lugar=Campus del Obelisco | https://www.tomaticket.es/es-es/entradas-aula-de-cine-los-angeles-del-pecado-en-las-palmas-de-gran-canaria
  - row 121 | EntradasCanarias | hora=19:00 | lugar=Salón de Actos del Edificio de Humanidades. Campus del Obelisco. | https://ventas.entradascanarias.com/events/aula-de-cine-los-angeles-del-pecado
- `carnival 2026 float parade` | fecha `2026-02-28` | count=2 | sources={'EntradasCanarias': 1, 'Tomaticket': 1}
  - row 126 | EntradasCanarias | hora=17:00 | lugar=Las Palmas GC Parade Carnival | https://ventas.entradascanarias.com/events/las-palmas-de-gran-canaria-carnival-2026-float-parade-tickets
  - row 128 | Tomaticket | hora=17:00 | lugar=Calle Doctor Juan Domínguez Pérez 1 | https://www.tomaticket.es/es-es/entradas-las-palmas-de-gran-canaria-carnival-2026-float-parade-tickets
- `lettering el arte de dibujar con letras` | fecha `2026-03-06` | count=2 | sources={'EntradasCanarias': 1, 'Tickety': 1}
  - row 148 | EntradasCanarias | hora=17:30 | lugar=Barbecho, laboratorio creativo | https://ventas.entradascanarias.com/events/lettering-el-arte-de-dibujar-con-letras
  - row 149 | Tickety | hora=17:30 | lugar=Barbecho | https://tickety.es/event/lettering-el-arte-de-dibujar-con-letras
- `aula de cine las damas del bosque de bolonia` | fecha `2026-03-06` | count=2 | sources={'Tomaticket': 1, 'EntradasCanarias': 1}
  - row 158 | Tomaticket | hora=19:00 | lugar=Campus del Obelisco | https://www.tomaticket.es/es-es/entradas-aula-de-cine-las-damas-del-bosque-de-bolonia-en-las-palmas-de-gran-canaria
  - row 159 | EntradasCanarias | hora=19:00 | lugar=Salón de Actos del Edificio de Humanidades. Campus del Obelisco. | https://ventas.entradascanarias.com/events/aula-de-cine-las-damas-del-bosque-de-bolonia
- `fito y fitipaldis aullidos tour 25 26` | fecha `2026-03-13` | count=2 | sources={'Entrées.es': 1, 'Ticketmaster': 1}
  - row 185 | Entrées.es | hora=20:00 | lugar=Gran Canaria | https://entrees.es/evento/ext/fito-y-fitipaldis-aullidos-tour-2526-en-las-palmas-de-gran-canaria-entradas
  - row 188 | Ticketmaster | hora=21:00 | lugar=Anexo Estadio de Gran Canaria | https://www.ticketmaster.es/event/fito--fitipaldis-aullidos-tour-25-26-tickets/446768384?language=en-us
- `aula de cine diario de un cura rural` | fecha `2026-03-13` | count=2 | sources={'EntradasCanarias': 1, 'Tomaticket': 1}
  - row 191 | EntradasCanarias | hora=19:00 | lugar=Salón de Actos del Edificio de Humanidades. Campus del Obelisco. | https://ventas.entradascanarias.com/events/aula-de-cine-diario-de-un-cura-rural
  - row 201 | Tomaticket | hora=19:00 | lugar=Salón de Actos del edificio de Humanidades. Campus del Obelisco. | https://www.tomaticket.es/es-es/entradas-aula-de-cine-diario-de-un-cura-rural-en-las-palmas-de-gran-canaria
- `lucho rk la pantera` | fecha `2026-03-14` | count=2 | sources={'Entrées.es': 1, 'Tomaticket': 1}
  - row 205 | Entrées.es | hora=20:00 | lugar=Gran Canaria | https://entrees.es/evento/ext/lucho-rk--la-pantera-en-gran-canaria-entradas
  - row 212 | Tomaticket | hora=21:00 | lugar=Estadio de Gran Canaria | https://www.tomaticket.es/es-es/entradas-lucho-rk-la-pantera-en-gran-canaria
- `la rose club 14 03 26` | fecha `2026-03-14` | count=2 | sources={'Tomaticket': 1, 'EntradasCanarias': 1}
  - row 207 | Tomaticket | hora=15:00 | lugar=Tienda Nankurunaisa, c.c Las Ramblas, Las Palmas de Gran Canaria | https://www.tomaticket.es/es-es/entradas-la-rose-club-140326-en-las-palmas-de-gran-canaria
  - row 208 | EntradasCanarias | hora=15:00 | lugar=Tienda Nankurunaisa, c.c Las Ramblas, Las Palmas de Gran Canaria | https://ventas.entradascanarias.com/events/la-rose-club-14-03-26-las-palmas-de-gran-canaria
- `el rey leoncio` | fecha `2026-03-20` | count=2 | sources={'CICCA': 1, 'Entrées.es': 1}
  - row 227 | CICCA | hora=20:30 | lugar=CICCA | https://www.fundacionlacajadecanarias.es/el-rey-leoncio/
  - row 229 | Entrées.es | hora=20:30 | lugar=Gran Canaria | https://entrees.es/evento/ext/el-rey-leoncio-en-gran-canaria-entradas
- `hades66` | fecha `2026-04-03` | count=2 | sources={'Entrées.es': 1, 'Tomaticket': 1}
  - row 267 | Entrées.es | hora=22:33 | lugar=Holiday World Maspalomas | https://entrees.es/evento/ext/hades66-en-gran-canaria-entradas
  - row 268 | Tomaticket | hora=19:00 | lugar=HolidayWorld Maspalomas | https://www.tomaticket.es/es-es/entradas-hades66-gran-canaria

### 1.4 Títulos sospechosos detectados (9)

| Row | Fuente | Fecha | Motivo | Título |
|---:|---|---|---|---|
| 110 | Tickety | 2026-02-26 | too_long | Aula Cultural De Ciencia & Gastronomía. "Comer Y Mostrar: La Gastronomía Entre El Arte, El Cine Y El Protocolo". III Foro Sobre Cultura, Gastronomía Y Cine |
| 130 | Entrées.es | 2026-02-28 | junk_token,too_short | Ext |
| 139 | Teatro Guiniguada | 2026-03-03 | too_long,many_numbers | Patrimonio Cultural El Milagro La Maldicion Y El Burro 494 145 218 526 984 228 980 379 996 187 688 403 303 787 989 915 472 |
| 177 | Tomaticket | 2026-03-11 | too_long | TALLER DE “CONCIENCIACIÓN SOBRE LA PÉRDIDA Y EL DESPERDICIO DE ALIMENTOS” Segunda edición (2026): pollo/gallina Palmas, Las |
| 179 | EntradasCanarias | 2026-03-11 | too_long | TALLER DE “CONCIENCIACIÓN SOBRE LA PÉRDIDA Y EL DESPERDICIO DE ALIMENTOS” Segunda edición (2026): pollo/gallina |
| 202 | EntradasCanarias | 2026-03-14 | truncated | Jorge Y... |
| 237 | Entrées.es | 2026-03-21 | junk_token,too_short | Ext |
| 376 | Entrées.es | 2026-07-02 | junk_token,too_short | Ext |
| 412 | EntradasCanarias | 2026-12-31 | too_long | Programa "Los 7 Pilares para un Liderazgo de Alto Impacto" (On Line, individual, mentorizado y comienzo personalizado) |

### 1.5 Lugares contaminados detectados (8)

| Row | Fuente | Fecha | Motivo | Lugar | Evento |
|---:|---|---|---|---|---|
| 5 | Entrées.es | 2025-11-07 | description_leak | paseo nocturno por Vegueta que no olvidarás | Free tour de los misterios y leyendas de Las Palmas de Gran Canaria |
| 9 | Entrées.es | 2025-11-20 | sentence_like,description_leak | plaza y prepárate para un día de lo más sabroso! | Tour gastronómico por Gran Canaria en Maspalomas |
| 33 | Entrées.es | 2025-12-16 | description_leak | calle y los gritos de sus vecinos le impiden dormir | LA MUJER ROTA en Gran Canaria |
| 37 | Entrées.es | 2025-12-17 | sentence_like,description_leak | plaza y descubre la cara más natural y auténtica de Gran Canaria! | Excursión a Teror, el Roque Nublo y la caldera de Bandama en Las Palmas de Gran Canaria |
| 179 | EntradasCanarias | 2026-03-11 | too_long | Lugar Aula de cocina del HUB GastroFood ULPGC Ubicación Facultad de Ciencias de la Salud Edificio Ciencias de la Salud Avda. Marítima del Sur s/n 35016 Las Palmas de Gran Canaria | TALLER DE “CONCIENCIACIÓN SOBRE LA PÉRDIDA Y EL DESPERDICIO DE ALIMENTOS” Segunda edición (2026): pollo/gallina |
| 202 | EntradasCanarias | 2026-03-14 | sentence_like | Distinto, Calle Miguel Rosas 21 | Jorge Y... |
| 207 | Tomaticket | 2026-03-14 | sentence_like | Tienda Nankurunaisa, c.c Las Ramblas, Las Palmas de Gran Canaria | LA ROSE CLUB - 14.03.26 en Las Palmas de Gran Canaria |
| 208 | EntradasCanarias | 2026-03-14 | sentence_like | Tienda Nankurunaisa, c.c Las Ramblas, Las Palmas de Gran Canaria | LA ROSE CLUB - 14.03.26 |

### 1.6 Horas sentinel/anómalas en Entrées

- Entrées total: **221**
- Hora `12:00`: **45**
- Hora `00:00`: **29**
- Hora `22:33`: **4**

---

## 2) Diagnóstico técnico (qué falta y por qué)

1. **Hora vacía > umbral**: faltan parseos robustos por fuente (especialmente Tomaticket/EntradasCanarias/CICCA).
2. **Dedupe incompleto**: persisten duplicados de misma fuente y cross-source; falta fase de consolidación final con scoring.
3. **Calidad semántica parcial**: siguen pasando títulos basura (`Ext`, `Jorge Y...`) y lugares contaminados por texto descriptivo.
4. **Export JSON no estricto**: hay `NaN` en `precio_num`; muchos parsers JSON estrictos fallarán.
5. **Control temporal no definido**: 26.7% de eventos son del pasado; falta política de recorte por ventana temporal.

---

## 3) Solución exacta (cambios puntuales por archivo)

## 3.1 `scrapers/main.py` — gates de calidad de cierre

### A) Gate de hora vacía
```python
pct_hora_vacia = df["hora"].isna().mean() * 100
if pct_hora_vacia > 7:
    raise RuntimeError(f"QA FAIL: hora vacía {pct_hora_vacia:.1f}% > 7%")
```

### B) Gate de títulos basura
```python
def es_titulo_basura(t: str) -> bool:
    t = (t or "").strip()
    low = t.lower()
    if low in {"ext", "nan", "none", "null", ""}: return True
    if len(t) <= 4: return True
    if len(t) >= 110: return True
    if re.search(r"\b\d{3}\b.*\b\d{3}\b", t): return True
    if t.endswith("..."): return True
    return False

df = df[~df["nombre"].apply(es_titulo_basura)]
```

### C) Sanitización de lugar
```python
def limpiar_lugar(lugar: str) -> str | None:
    l = (lugar or "").strip()
    leak_tokens = ["paseo nocturno", "prepárate", "descubre", "que no olvidarás", "la cara más natural"]
    if len(l) > 70: return None
    if any(tok in l.lower() for tok in leak_tokens): return None
    return l or None

df["lugar"] = df["lugar"].apply(limpiar_lugar)
```

## 3.2 `scrapers/main.py` — dedupe final robusto (incluye consolidación cross-source)

1) Mantener dedupe por clave compuesta (`titulo_norm+fecha+venue+hora`).
2) Añadir fase final por `canonical+fecha` con scoring de calidad para elegir un ganador.

```python
PREF = {"Ticketmaster": 100, "EntradasCanarias": 90, "Tickety": 80, "Tomaticket": 70, "CICCA": 65, "Teatro Guiniguada": 65, "Entrées.es": 40}

def quality_score(r):
    s = PREF.get(r["organiza"], 50)
    s += 10 if pd.notna(r["hora"]) and str(r["hora"]).strip() else 0
    s += 10 if pd.notna(r["precio_num"]) else 0
    s += 10 if pd.notna(r["lugar"]) and str(r["lugar"]).strip() else 0
    return s

df["_canon"] = df["nombre"].apply(normalizar_titulo)
df["_score"] = df.apply(quality_score, axis=1)
df = df.sort_values(["_canon", "fecha_iso", "_score"], ascending=[True, True, False])
df = df.drop_duplicates(subset=["_canon", "fecha_iso"], keep="first")
```

## 3.3 `scrapers/app/scrapers/entradas_canarias.py`

- En API, priorizar `sessions[].date` para poblar hora exacta (`HH:MM`) en vez de fallback nulo.
- Unificar eventos duplicados de la misma fuente por `masterId + fecha`.

```python
for sess in item.get("sessions", []):
    dt = parse_iso(sess.get("date"))
    fecha_iso = dt.date().isoformat()
    hora = dt.strftime("%H:%M") if dt else None
    key = (item.get("masterId"), fecha_iso)
```

## 3.4 `scrapers/app/scrapers/tomaticket.py`

- Añadir parse de hora desde JSON-LD / meta / detalle (hoy hay 17 nulos).
- Evitar defaults ambiguos (`00:00`) cuando no hay hora real.

## 3.5 `scrapers/app/scrapers/_enrichment.py`

- Extender normalización de hora para descartar `22:33` cuando provenga de metadatos de publicación y no de evento real.
- Si hora parece inválida por patrón fuente, dejar `None` para no contaminar.

## 3.6 `scrapers/upload_to_supabase.py` (o `scripts/excel_to_supabase.py`)

### Problema
Hay 32 tokens `NaN` en JSON (no estricto).

### Fix exacto
```python
def none_if_nan(v):
    if isinstance(v, float) and math.isnan(v):
        return None
    return v

for row in rows:
    row["precio_num"] = none_if_nan(row.get("precio_num"))

json.dump(rows, f, ensure_ascii=False, indent=2, allow_nan=False)
```

## 3.7 Política temporal (decisión de producto)

- Si el objetivo es agenda futura, recortar en `main.py`:
```python
today = datetime.date.today()
df = df[df["fecha_iso"] >= today.isoformat()]
```
- Esto elimina 110 eventos pasados del último dump.

---

## 4) Plan de ejecución exacto (48h)

### Día 1 (P0/P1)
1. Implementar gates en `main.py` (hora vacía, título basura, lugar contaminado).
2. Implementar dedupe de consolidación final `canonical+fecha` con scoring.
3. Corregir `entradas_canarias.py` para hora por `sessions[].date` + dedupe interno `masterId+fecha`.
4. Corregir `upload_to_supabase.py` para `NaN -> null` + `allow_nan=False`.

### Día 2 (P1/P2)
5. Mejorar parse de hora en `tomaticket.py` y limpieza en `_enrichment.py` de horas sentinel.
6. Ejecutar barrido completo y regenerar evidencia + excels.
7. Reauditar contra KPIs de cierre.

---

## 5) Criterios de cierre (hard pass)

- Hora vacía <= 7%
- Títulos basura = 0
- Lugares contaminados = 0
- Duplicados misma fuente (`canonical+fecha`) = 0
- JSON estricto: `NaN tokens = 0`
- (Opcional producto) Eventos pasados recortados si agenda es futura

---

## 6) Nota sobre `evidence_report.md` recibido

- El informe reporta “completamente limpios”, pero los datos actuales aún muestran pendientes medibles.
- También aparece el mensaje “fecha inválida 2026-02-14”; esa fecha es válida ISO.
- Recomendación: usar este informe como checklist técnico de cierre real.
