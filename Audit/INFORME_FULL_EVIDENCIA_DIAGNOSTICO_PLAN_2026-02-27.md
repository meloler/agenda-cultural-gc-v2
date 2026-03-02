# INFORME FULL — Evidencia completa, diagnóstico técnico y plan de ejecución

**Fecha generación:** 2026-02-27 04:37 UTC  
**Base de análisis:** Excel históricos + Excel nuevos + código de scrapers + validación web en vivo (Playwright/requests).

---

## 1) EVIDENCIA COMPLETA

### 1.1 Inventario de artefactos analizados

#### Excel analizados
- `file_34---...xlsx` (borrador anterior)
- `file_35---...xlsx` (limpio anterior)
- `file_39---...xlsx` (borrador nuevo)
- `file_40---...xlsx` (limpio nuevo)

#### Módulos de scraping/pipeline analizados (nombres reales)
- `app/main.py`
- `app/scrapers/tomaticket.py`
- `app/scrapers/cultura_canaria.py`
- `app/scrapers/entradas_canarias.py`
- `app/scrapers/entradas_com.py`
- `app/scrapers/entrees.py`
- `app/scrapers/institucional.py`
- `app/scrapers/telde_cultura.py`
- `app/scrapers/ticketmaster_api.py`
- `app/scrapers/ticketmaster_web.py`
- `app/scrapers/tickety.py`
- `app/auditor.py`
- `app/classifier.py`
- `app/cleaner.py`
- `app/enricher.py`
- `app/geocoder.py`
- `app/scrapers/_enrichment.py`
- `app/database.py`
- `app/models.py`
- `app/crud.py`
- `scripts/excel_to_supabase.py`

### 1.2 Métricas completas de Excel (global)

| Dataset | Filas | Fecha vacía | Hora vacía | Precio vacío | URL vacía | Imagen vacía | Títulos truncados (...) | Desc `[Generado por IA]` | Títulos genéricos |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BORRADOR anterior (file_34) | 13 | 13 (100.0%) | 9 (69.2%) | 9 (69.2%) | 0 (0.0%) | 1 (7.7%) | 0 | 3 | 0 |
| BORRADOR nuevo (file_39) | 6 | 6 (100.0%) | 5 (83.3%) | 4 (66.7%) | 0 (0.0%) | 2 (33.3%) | 0 | 2 | 2 |
| LIMPIO anterior (file_35) | 333 | 0 (0.0%) | 21 (6.3%) | 41 (12.3%) | 0 (0.0%) | 0 (0.0%) | 32 | 44 | 0 |
| LIMPIO nuevo (file_40) | 227 | 0 (0.0%) | 21 (9.3%) | 37 (16.3%) | 0 (0.0%) | 0 (0.0%) | 0 | 15 | 119 |

### 1.3 Filas exactas con faltantes y anomalías (datasets limpios)

#### LIMPIO anterior (file_35)
- Sin precio (41):
```
3,70,106,108,110,112,113,115,117,118,119,120,126,128,130,134,137,140,151,152,155,156,157,159,160,162,166,167,177,180,184,186,193,197,205,214,225,231,241,323,327
```
- Sin hora (21):
```
70,83,84,90,95,97,100,101,116,126,146,150,172,182,217,219,300,312,313,327,333
```

#### LIMPIO nuevo (file_40)
- Sin precio (37):
```
3,35,62,65,66,68,69,71,72,74,76,80,81,84,87,91,95,96,97,100,101,103,105,108,115,116,122,123,125,129,133,141,148,153,161,217,221
```
- Sin hora (21):
```
35,42,43,49,51,56,58,59,70,77,90,99,111,121,143,144,198,207,208,221,227
```
- Título genérico (119):
```
2,5,6,7,8,9,10,11,12,14,15,17,18,19,20,21,22,24,25,26,27,28,29,30,32,33,34,36,37,38,39,40,48,61,64,67,78,79,88,92,98,104,106,110,114,118,124,128,130,132,134,137,138,140,142,145,146,149,150,151,152,155,157,158,160,163,164,165,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,191,192,193,194,195,196,197,199,200,202,203,204,205,208,209,211,212,213,214,215,216,218,220,222,223,224,225,226,228
```

### 1.4 Duplicados detallados (datasets limpios)

#### LIMPIO anterior (file_35)
- Grupos por nombre canonical: **23**
- Confirmados misma fecha: **15**
- Series (fechas distintas): **8**

##### Grupos confirmados (misma fecha)
1. `acis y galatea` (2 filas)
   - row 231 | Acis Y Galatea | fecha=2026-04-02 | hora=19:00 | lugar=Teatro Pérez Galdós | fuente=Teatro Pérez Galdós
   - row 232 | Acis y Galatea en Gran Canaria | fecha=2026-04-02 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
2. `cartas a nestor` (2 filas)
   - row 159 | Cartas A Nestor | fecha=2026-03-07 | hora=20:00 | lugar=Teatro Pérez Galdós | fuente=Teatro Pérez Galdós
   - row 161 | Cartas a Néstor en Gran Canaria | fecha=2026-03-07 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
3. `concentus musicus wien` (2 filas)
   - row 204 | Concentus Musicus Wien en Gran Canaria | fecha=2026-03-20 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 205 | Concentus Musicus Wien | fecha=2026-03-20 | hora=20:00 | lugar=Teatro Pérez Galdós | fuente=Teatro Pérez Galdós
4. `diana navarro` (2 filas)
   - row 120 | Diana Navarro | fecha=2026-02-28 | hora=20:00 | lugar=Auditorio A. Kraus | fuente=Auditorio A. Kraus
   - row 125 | Diana Navarro en Gran Canaria | fecha=2026-02-28 | hora=20:00 | lugar=Auditorio Alfredo Kraus | fuente=Entrées.es
5. `donde esta alicia` (2 filas)
   - row 238 | ¿Dónde está Alicia? en Gran Canaria | fecha=2026-04-10 | hora=19:00 | lugar=Teatro Pérez Galdós | fuente=Entrées.es
   - row 241 | Donde Esta Alicia | fecha=2026-04-10 | hora=19:00 | lugar=Teatro Pérez Galdós | fuente=Teatro Pérez Galdós
6. `el rey leoncio` (2 filas)
   - row 203 | El Rey Leoncio | fecha=2026-03-20 | hora=20:30 | lugar=CICCA | fuente=CICCA
   - row 206 | El Rey Leoncio en Gran Canaria | fecha=2026-03-20 | hora=20:30 | lugar=Gran Canaria | fuente=Entrées.es
7. `georgina` (2 filas)
   - row 165 | Georgina en Gran Canaria | fecha=2026-03-07 | hora=20:30 | lugar=Auditorio Alfredo Kraus | fuente=Entrées.es
   - row 166 | Georgina | fecha=2026-03-07 | hora=20:30 | lugar=Auditorio A. Kraus | fuente=Auditorio A. Kraus
8. `javier santaolalla el club de la tusa que es el tiempo` (2 filas)
   - row 224 | Javier Santaolalla. El Club de la Tusa. ¿Qué es el tiempo? en Gran Canaria | fecha=2026-03-28 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 225 | Javier Santaolalla El Club De La Tusa Que Es El Tiempo | fecha=2026-03-28 | hora=20:00 | lugar=Teatro Pérez Galdós | fuente=Teatro Pérez Galdós
9. `los cuernos de don friolera` (2 filas)
   - row 144 | Los cuernos de don Friolera en Gran Canaria | fecha=2026-03-06 | hora=20:00 | lugar=Teatro Pérez Galdós | fuente=Entrées.es
   - row 156 | Los Cuernos De Don Friolera | fecha=2026-03-06 | hora=20:00 | lugar=Teatro Pérez Galdós | fuente=Teatro Pérez Galdós
10. `otello` (2 filas)
   - row 214 | Otello | fecha=2026-03-24 | hora=20:00 | lugar=Teatro Pérez Galdós | fuente=Teatro Pérez Galdós
   - row 215 | OTELLO en Gran Canaria | fecha=2026-03-24 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
11. `poliedro de amor` (2 filas)
   - row 114 | Poliedro de amor en Gran Canaria | fecha=2026-02-27 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 119 | Poliedro De Amor | fecha=2026-02-27 | hora=20:00 | lugar=Teatro Pérez Galdós | fuente=Teatro Pérez Galdós
12. `resilientes` (2 filas)
   - row 167 | Resilientes | fecha=2026-03-08 | hora=18:00 | lugar=Auditorio A. Kraus | fuente=Auditorio A. Kraus
   - row 168 | Resilientes en Gran Canaria | fecha=2026-03-08 | hora=18:00 | lugar=Gran Canaria | fuente=Entrées.es
13. `senora einstein` (2 filas)
   - row 183 | Señora Einstein en Gran Canaria | fecha=2026-03-13 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 184 | Senora Einstein | fecha=2026-03-13 | hora=20:00 | lugar=Teatro Pérez Galdós | fuente=Teatro Pérez Galdós
14. `soy salvaje` (2 filas)
   - row 132 | ¡Soy Salvaje! en Gran Canaria | fecha=2026-03-01 | hora=18:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 134 | Soy Salvaje | fecha=2026-03-01 | hora=18:00 | lugar=Teatro Pérez Galdós | fuente=Teatro Pérez Galdós
15. `te toca moving concerts` (2 filas)
   - row 195 | Te Toca. Moving Concerts en Gran Canaria | fecha=2026-03-15 | hora=18:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 197 | Te Toca Moving Concerts | fecha=2026-03-15 | hora=18:00 | lugar=Auditorio A. Kraus | fuente=Auditorio A. Kraus

##### Grupos serie (mismo nombre, fecha distinta)
1. `disparate un show de omayra cazorla` (2 filas)
   - row 61 | DISPARATE. UN SHOW DE OMAYRA CAZORLA en Gran Canaria | fecha=2026-01-16 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 316 | Disparate Un Show De Omayra Cazorla | fecha=2026-07-24 | hora=20:30 | lugar=CICCA | fuente=CICCA
2. `granca live fest 2026` (2 filas)
   - row 219 | GRANCA Live Fest 2026 | fecha=2026-03-26 | hora= | lugar=Estadio de Gran Canaria | fuente=Tomaticket
   - row 305 | GRANCA Live Fest 2026 en LAS PALMAS DE GRAN CANARIA | fecha=2026-07-02 | hora=00:00 | lugar=Gran Canaria | fuente=Entrées.es
3. `idols la revolucion k pop las guerreras del ritmo` (3 filas)
   - row 12 | IDOLS. LA REVOLUCIÓN K-POP. LAS GUERRERAS DEL RITMO (16:30 H.) en Gran Canaria | fecha=2025-11-24 | hora=09:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 14 | IDOLS. LA REVOLUCIÓN K-POP. LAS GUERRERAS DEL RITMO (19:00 H.) en Gran Canaria | fecha=2025-12-03 | hora=10:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 315 | IDOLS. LA REVOLUCIÓN K-POP. LAS GUERRERAS DEL RITMO en Gran Canaria | fecha=2026-07-18 | hora=16:30 | lugar=Gran Canaria | fuente=Entrées.es
4. `la oreja de van gogh` (2 filas)
   - row 324 | La Oreja de Van Gogh en LAS PALMAS DE GRAN CANARIA | fecha=2026-10-23 | hora=00:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 334 | La Oreja de Van Gogh en Gran Canaria | fecha=2027-10-23 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
5. `la pasion segun san juan` (2 filas)
   - row 140 | La Pasion Segun San Juan Top 5 | fecha=2026-03-05 | hora=20:00 | lugar=Auditorio A. Kraus | fuente=Auditorio A. Kraus
   - row 157 | La Pasion Segun San Juan | fecha=2026-03-06 | hora=20:00 | lugar=Auditorio A. Kraus | fuente=Auditorio A. Kraus
6. `la reina de las nieves` (2 filas)
   - row 43 | La Reina De Las Nieves | fecha=2025-12-30 | hora=12:30 | lugar=CICCA | fuente=CICCA
   - row 62 | LA REINA DE LAS NIEVES en Gran Canaria | fecha=2026-01-16 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
7. `las noches con cristito y la madre canaria` (2 filas)
   - row 63 | Las Noches Con Cristito Y La Madre Canaria | fecha=2026-01-17 | hora=20:00 | lugar=CICCA | fuente=CICCA
   - row 76 | LAS NOCHES CON CRISTITO Y LA MADRE CANARIA en Gran Canaria | fecha=2026-01-28 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
8. `the jury experience muerte por ia quien paga el precio` (2 filas)
   - row 81 | The Jury Experience – Muerte por IA: ¿Quién Paga el precio? en Las Palmas de Gran Canaria | fecha=2026-01-30 | hora=18:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 228 | The Jury Experience: Muerte por IA: ¿Quién Paga el precio? en Las Palmas de Gran Canaria | fecha=2026-03-29 | hora=17:00 | lugar=Gran Canaria | fuente=Entrées.es

##### Pares fuzzy relevantes: 8
- score 97.0 | same_date=True | same_place=False | contain=False
  - A row 177: Andrea Motis La Perinke Big Band (2026-03-13, Auditorio A. Kraus, Auditorio A. Kraus)
  - B row 181: ANDREA MOTIS & LA PERINKÉ BIG BAND en Gran Canaria (2026-03-13, Gran Canaria, Entrées.es)
- score 96.7 | same_date=True | same_place=False | contain=True
  - A row 151: Aula De Cine. "Las Damas Del Bosque De Bolonia" (2026-03-06, Campus del Obelisco, Tickety)
  - B row 152: Aula de cine. "Las damas del bosque de Bolonia" en... (2026-03-06, Salón de Actos del edificio de Humanidades. Campus del Obelisco., Tomaticket)
- score 95.4 | same_date=True | same_place=False | contain=False
  - A row 244: Adulto En Practicas De Himar Armas (2026-04-11, CICCA, CICCA)
  - B row 247: Adulto en Prácticas - Himar Armas en Gran Canaria (2026-04-11, Gran Canaria, Entrées.es)
- score 94.1 | same_date=True | same_place=False | contain=True
  - A row 124: Entradas Carroza Cabalgata Carnaval Las Palmas GC ... (2026-02-28, Cabalgata de Las Palmas de Gran Canaria 2026, Tomaticket)
  - B row 128: Entradas Carroza Cabalgata Carnaval Las Palmas GC 2026 (2026-02-28, Calle Doctor Juan Domínguez Pérez 1, Tickety)
- score 93.3 | same_date=False | same_place=False | contain=True
  - A row 89: Entrada al acuario Poema del Mar en Las Palmas de Gran Canaria (2026-02-16, paseo de la Playa de las Canteras, Entrées.es)
  - B row 95: Acuario Poema del Mar Gran Canaria (2026-02-23, Acuario Poema del Mar, Tomaticket)
- score 90.0 | same_date=True | same_place=False | contain=True
  - A row 108: Encuentro Bitácora: CONVIÉRTETE EN EL LÍDER DE TU EQUIPO (2026-02-26, Calle Juan de Quesada, Tickety)
  - B row 109: Encuentro Bitácora: CONVIÉRTETE EN EL LÍDER DE ... (2026-02-26, Coworking Hashtag, Tomaticket)
- score 88.7 | same_date=True | same_place=False | contain=False
  - A row 148: SUPERSAURIO, EL MUSICAL de Meryem El Mehdati en Gran Canaria en Las Palmas (2026-03-06, Gran Canaria, Entrées.es)
  - B row 150: SUPERSAURIO, EL MUSICAL de Meryem El Mehdati en Gr... (2026-03-06, Teatro Cuyás, Tomaticket)
- score 88.6 | same_date=False | same_place=False | contain=True
  - A row 68: Candlelight: Lo Mejor de Ennio Morricone en Las Palmas de Gran Canaria (2026-01-21, Gran Canaria, Entrées.es)
  - B row 98: Candlelight: Lo Mejor de Ennio Morricone en Las Pa... (2026-02-23, Gabinete Literario, Tomaticket)

#### LIMPIO nuevo (file_40)
- Grupos por nombre canonical: **3**
- Confirmados misma fecha: **0**
- Series (fechas distintas): **3**

##### Grupos serie (mismo nombre, fecha distinta)
1. `for the best events` (3 filas)
   - row 98 | Tickets for the best events | fecha=2026-03-06 | hora=19:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 138 | Tickets for the best events | fecha=2026-03-21 | hora=17:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 186 | Tickets for the best events | fecha=2026-05-29 | hora=19:30 | lugar=Gran Canaria | fuente=Entrées.es
2. `la pasion segun san juan` (2 filas)
   - row 87 | La Pasion Segun San Juan Top 5 | fecha=2026-03-05 | hora=20:00 | lugar=Auditorio A. Kraus | fuente=Auditorio A. Kraus
   - row 95 | La Pasion Segun San Juan | fecha=2026-03-06 | hora=20:00 | lugar=Auditorio A. Kraus | fuente=Auditorio A. Kraus
3. `para los mejores eventos` (116 filas)
   - row 2 | Entradas para los mejores eventos | fecha=2019-07-04 | hora=10:00 | lugar=Palmitos Park | fuente=Entrées.es
   - row 5 | Entradas para los mejores eventos | fecha=2025-08-29 | hora=21:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 6 | Entradas para los mejores eventos | fecha=2025-11-07 | hora=00:00 | lugar=paseo nocturno por Vegueta que no olvidarás | fuente=Entrées.es
   - row 7 | Entradas para los mejores eventos | fecha=2025-11-20 | hora=00:00 | lugar=plaza y prepárate para un día de lo más sabroso! | fuente=Entrées.es
   - row 8 | Entradas para los mejores eventos | fecha=2025-11-22 | hora=00:00 | lugar=Auditorio Alfredo Kraus | fuente=Entrées.es
   - row 9 | Entradas para los mejores eventos | fecha=2025-11-24 | hora=09:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 10 | Entradas para los mejores eventos | fecha=2025-12-02 | hora=00:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 11 | Entradas para los mejores eventos | fecha=2025-12-03 | hora=10:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 12 | Entradas para los mejores eventos | fecha=2025-12-05 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 14 | Entradas para los mejores eventos | fecha=2025-12-10 | hora=14:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 15 | Entradas para los mejores eventos | fecha=2025-12-12 | hora=00:00 | lugar=Teatro Pérez Galdós | fuente=Entrées.es
   - row 17 | Entradas para los mejores eventos | fecha=2025-12-14 | hora=00:00 | lugar=paseo marítimo | fuente=Entrées.es
   - row 18 | Entradas para los mejores eventos | fecha=2025-12-15 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 19 | Entradas para los mejores eventos | fecha=2025-12-16 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 20 | Entradas para los mejores eventos | fecha=2025-12-17 | hora=00:00 | lugar=plaza y descubre la cara más natural y auténtica de Gran Canaria! | fuente=Entrées.es
   - row 21 | Entradas para los mejores eventos | fecha=2025-12-18 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 22 | Entradas para los mejores eventos | fecha=2025-12-26 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 24 | Entradas para los mejores eventos | fecha=2026-01-02 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 25 | Entradas para los mejores eventos | fecha=2026-01-08 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 26 | Entradas para los mejores eventos | fecha=2026-01-09 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 27 | Entradas para los mejores eventos | fecha=2026-01-10 | hora=17:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 28 | Entradas para los mejores eventos | fecha=2026-01-12 | hora=00:00 | lugar=Casa de Colón | fuente=Entrées.es
   - row 29 | Entradas para los mejores eventos | fecha=2026-01-14 | hora=12:00 | lugar=Nuevo Teatro Viejo de Arucas | fuente=Entrées.es
   - row 30 | Entradas para los mejores eventos | fecha=2026-01-16 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 32 | Entradas para los mejores eventos | fecha=2026-01-19 | hora=00:00 | lugar=Casa de Colón | fuente=Entrées.es
   - row 33 | Entradas para los mejores eventos | fecha=2026-01-20 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 34 | Entradas para los mejores eventos | fecha=2026-01-21 | hora=21:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 36 | Entradas para los mejores eventos | fecha=2026-01-26 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 37 | Entradas para los mejores eventos | fecha=2026-01-27 | hora=00:00 | lugar=calle Herrería para arrancar nuestra visita guiada por el barrio d | fuente=Entrées.es
   - row 38 | Entradas para los mejores eventos | fecha=2026-01-28 | hora=12:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 39 | Entradas para los mejores eventos | fecha=2026-01-30 | hora=18:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 40 | Entradas para los mejores eventos | fecha=2026-02-04 | hora=16:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 48 | Entradas para los mejores eventos | fecha=2026-02-16 | hora=00:00 | lugar=paseo de la Playa de las Canteras | fuente=Entrées.es
   - row 61 | Entradas para los mejores eventos | fecha=2026-02-25 | hora=09:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 64 | Entradas para los mejores eventos | fecha=2026-02-26 | hora=10:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 67 | Entradas para los mejores eventos | fecha=2026-02-27 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 78 | Entradas para los mejores eventos | fecha=2026-02-28 | hora=17:00 | lugar=Calle Doctor Juan Domínguez Pérez 1 | fuente=Entrées.es
   - row 79 | Entradas para los mejores eventos | fecha=2026-03-01 | hora=18:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 88 | Entradas para los mejores eventos | fecha=2026-03-05 | hora=19:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 92 | Entradas para los mejores eventos | fecha=2026-03-06 | hora=00:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 104 | Entradas para los mejores eventos | fecha=2026-03-07 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 106 | Entradas para los mejores eventos | fecha=2026-03-08 | hora=18:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 110 | Entradas para los mejores eventos | fecha=2026-03-10 | hora=19:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 114 | Entradas para los mejores eventos | fecha=2026-03-12 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 118 | Entradas para los mejores eventos | fecha=2026-03-13 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 124 | Entradas para los mejores eventos | fecha=2026-03-14 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 128 | Entradas para los mejores eventos | fecha=2026-03-15 | hora=20:00 | lugar=Talleres Palermo | fuente=Entrées.es
   - row 130 | Entradas para los mejores eventos | fecha=2026-03-18 | hora=20:00 | lugar=Auditorio Alfredo Kraus | fuente=Entrées.es
   - row 132 | Entradas para los mejores eventos | fecha=2026-03-19 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 134 | Entradas para los mejores eventos | fecha=2026-03-20 | hora=19:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 137 | Entradas para los mejores eventos | fecha=2026-03-21 | hora=17:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 140 | Entradas para los mejores eventos | fecha=2026-03-24 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 142 | Entradas para los mejores eventos | fecha=2026-03-25 | hora=00:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 145 | Entradas para los mejores eventos | fecha=2026-03-26 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 146 | Entradas para los mejores eventos | fecha=2026-03-27 | hora=20:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 149 | Entradas para los mejores eventos | fecha=2026-03-28 | hora=19:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 150 | Entradas para los mejores eventos | fecha=2026-03-29 | hora=12:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 151 | Entradas para los mejores eventos | fecha=2026-03-30 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 152 | Entradas para los mejores eventos | fecha=2026-04-02 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 155 | Entradas para los mejores eventos | fecha=2026-04-03 | hora=22:33 | lugar=Holiday World Maspalomas | fuente=Entrées.es
   - row 157 | Entradas para los mejores eventos | fecha=2026-04-04 | hora=18:04 | lugar=Gran Canaria | fuente=Entrées.es
   - row 158 | Entradas para los mejores eventos | fecha=2026-04-09 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 160 | Entradas para los mejores eventos | fecha=2026-04-10 | hora=19:00 | lugar=Teatro Pérez Galdós | fuente=Entrées.es
   - row 163 | Entradas para los mejores eventos | fecha=2026-04-11 | hora=20:00 | lugar=Sala Alboroto | fuente=Entrées.es
   - row 164 | Entradas para los mejores eventos | fecha=2026-04-12 | hora=19:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 165 | Entradas para los mejores eventos | fecha=2026-04-17 | hora=20:00 | lugar=Auditorio Alfredo Kraus | fuente=Entrées.es
   - row 168 | Entradas para los mejores eventos | fecha=2026-04-18 | hora=00:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 169 | Entradas para los mejores eventos | fecha=2026-04-21 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 170 | Entradas para los mejores eventos | fecha=2026-04-23 | hora=19:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 171 | Entradas para los mejores eventos | fecha=2026-04-24 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 172 | Entradas para los mejores eventos | fecha=2026-04-25 | hora=18:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 173 | Entradas para los mejores eventos | fecha=2026-04-26 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 174 | Entradas para los mejores eventos | fecha=2026-04-30 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 175 | Entradas para los mejores eventos | fecha=2026-05-01 | hora=20:00 | lugar=Auditorio Alfredo Kraus | fuente=Entrées.es
   - row 176 | Entradas para los mejores eventos | fecha=2026-05-02 | hora=22:33 | lugar=Auditorio Parque San Juan | fuente=Entrées.es
   - row 177 | Entradas para los mejores eventos | fecha=2026-05-03 | hora=19:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 178 | Entradas para los mejores eventos | fecha=2026-05-08 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 179 | Entradas para los mejores eventos | fecha=2026-05-09 | hora=18:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 180 | Entradas para los mejores eventos | fecha=2026-05-10 | hora=19:00 | lugar=Auditorio Alfredo Kraus | fuente=Entrées.es
   - row 181 | Entradas para los mejores eventos | fecha=2026-05-16 | hora=19:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 182 | Entradas para los mejores eventos | fecha=2026-05-19 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 183 | Entradas para los mejores eventos | fecha=2026-05-22 | hora=20:30 | lugar=Anexo Estadio Gran Canaria | fuente=Entrées.es
   - row 184 | Entradas para los mejores eventos | fecha=2026-05-23 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 185 | Entradas para los mejores eventos | fecha=2026-05-29 | hora=19:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 187 | Entradas para los mejores eventos | fecha=2026-06-05 | hora=19:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 188 | Entradas para los mejores eventos | fecha=2026-06-06 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 189 | Entradas para los mejores eventos | fecha=2026-06-07 | hora=19:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 191 | Entradas para los mejores eventos | fecha=2026-06-11 | hora=23:00 | lugar=Ciudad Deportiva de Maspalomas | fuente=Entrées.es
   - row 192 | Entradas para los mejores eventos | fecha=2026-06-12 | hora=19:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 193 | Entradas para los mejores eventos | fecha=2026-06-13 | hora=20:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 194 | Entradas para los mejores eventos | fecha=2026-06-14 | hora=18:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 195 | Entradas para los mejores eventos | fecha=2026-06-16 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 196 | Entradas para los mejores eventos | fecha=2026-06-17 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 197 | Entradas para los mejores eventos | fecha=2026-06-19 | hora=19:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 199 | Entradas para los mejores eventos | fecha=2026-06-26 | hora=00:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 200 | Entradas para los mejores eventos | fecha=2026-06-27 | hora=20:00 | lugar=Auditorio Alfredo Kraus | fuente=Entrées.es
   - row 202 | Entradas para los mejores eventos | fecha=2026-07-02 | hora=00:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 203 | Entradas para los mejores eventos | fecha=2026-07-04 | hora=08:56 | lugar=Gran Canaria | fuente=Entrées.es
   - row 204 | Entradas para los mejores eventos | fecha=2026-07-09 | hora=00:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 205 | Entradas para los mejores eventos | fecha=2026-07-10 | hora=22:33 | lugar=Auditorio Parque San Juan | fuente=Entrées.es
   - row 208 | Entradas para los mejores eventos | fecha=2026-07-11 | hora= | lugar=Estadio de Gran Canaria | fuente=Entrées.es
   - row 209 | Entradas para los mejores eventos | fecha=2026-07-18 | hora=16:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 211 | Entradas para los mejores eventos | fecha=2026-07-24 | hora=20:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 212 | Entradas para los mejores eventos | fecha=2026-07-26 | hora=21:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 213 | Entradas para los mejores eventos | fecha=2026-07-31 | hora=21:00 | lugar=Gran Canaria Arena | fuente=Entrées.es
   - row 214 | Entradas para los mejores eventos | fecha=2026-08-01 | hora=18:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 215 | Entradas para los mejores eventos | fecha=2026-08-21 | hora=19:30 | lugar=Gran Canaria | fuente=Entrées.es
   - row 216 | Entradas para los mejores eventos | fecha=2026-10-02 | hora=22:33 | lugar=Gran Canaria | fuente=Entrées.es
   - row 218 | Entradas para los mejores eventos | fecha=2026-10-23 | hora=00:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 220 | Entradas para los mejores eventos | fecha=2026-11-01 | hora=19:00 | lugar=Auditorio Alfredo Kraus | fuente=Entrées.es
   - row 222 | Entradas para los mejores eventos | fecha=2026-11-08 | hora=19:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 223 | Entradas para los mejores eventos | fecha=2026-11-14 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 224 | Entradas para los mejores eventos | fecha=2026-12-05 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 225 | Entradas para los mejores eventos | fecha=2026-12-07 | hora=00:00 | lugar=Gran Canaria | fuente=Entrées.es
   - row 226 | Entradas para los mejores eventos | fecha=2026-12-08 | hora=19:00 | lugar=Auditorio Alfredo Kraus | fuente=Entrées.es
   - row 228 | Entradas para los mejores eventos | fecha=2027-10-23 | hora=20:00 | lugar=Gran Canaria | fuente=Entrées.es

##### Pares fuzzy relevantes: 0

### 1.5 Calidad por fuente (datasets limpios)

#### LIMPIO anterior (file_35)
| Fuente | Total | Sin precio | Sin hora | Título genérico |
|---|---:|---:|---:|---:|
| Entrées.es | 213 | 0 (0.0%) | 1 (0.5%) | 0 (0.0%) |
| Tomaticket | 56 | 7 (12.5%) | 17 (30.4%) | 0 (0.0%) |
| CICCA | 18 | 3 (16.7%) | 3 (16.7%) | 0 (0.0%) |
| Tickety | 15 | 9 (60.0%) | 0 (0.0%) | 0 (0.0%) |
| Auditorio A. Kraus | 10 | 10 (100.0%) | 0 (0.0%) | 0 (0.0%) |
| Teatro Pérez Galdós | 10 | 10 (100.0%) | 0 (0.0%) | 0 (0.0%) |
| Teatro Guiniguada | 8 | 1 (12.5%) | 0 (0.0%) | 0 (0.0%) |
| Ticketmaster | 2 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| TeldeCultura | 1 | 1 (100.0%) | 0 (0.0%) | 0 (0.0%) |

#### LIMPIO nuevo (file_40)
| Fuente | Total | Sin precio | Sin hora | Título genérico |
|---|---:|---:|---:|---:|
| Entrées.es | 119 | 0 (0.0%) | 1 (0.8%) | 119 (100.0%) |
| Tomaticket | 52 | 6 (11.5%) | 17 (32.7%) | 0 (0.0%) |
| CICCA | 18 | 3 (16.7%) | 3 (16.7%) | 0 (0.0%) |
| Auditorio A. Kraus | 10 | 10 (100.0%) | 0 (0.0%) | 0 (0.0%) |
| Teatro Pérez Galdós | 10 | 10 (100.0%) | 0 (0.0%) | 0 (0.0%) |
| Teatro Guiniguada | 8 | 1 (12.5%) | 0 (0.0%) | 0 (0.0%) |
| Tickety | 7 | 6 (85.7%) | 0 (0.0%) | 0 (0.0%) |
| Ticketmaster | 2 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| TeldeCultura | 1 | 1 (100.0%) | 0 (0.0%) | 0 (0.0%) |

### 1.6 Evidencia de estructura web por portal (runtime desde VPS)

| Módulo | URL | Estado | Título página | Selectores observados |
|---|---|---|---|---|
| `cultura_canaria:auditorio` | https://auditorioalfredokraus.es/programacion | ✅ Accesible | Programación - Auditorio Alfredo Kraus | a[href*="/evento/"]:21, a[href*="/evento-"]:0 |
| `cultura_canaria:perez_galdos` | https://teatroperezgaldos.es/programacion | ✅ Accesible | Programación - Teatro Pérez Galdós | a[href*="/evento/"]:20, a[href*="/evento-"]:0 |
| `entradas_canarias` | https://entradascanarias.com/ | ✅ Accesible | entradascanarias.com   Tu plataforma de organización y compra de entradas en Canarias | h5:38, button:has-text("Cargar más"):1, .card:37, a[href*="buy"]:0, a[href*="event"]:0 |
| `entradas_com` | https://www.entradas.com/search/?affiliate=EES&searchterm=Gran+canaria | ❌ Error | - | `Page.goto: net::ERR_HTTP2_PROTOCOL_ERROR at https://www.entradas.com/search/?affiliate=EES&searchterm=Gran+canaria` |
| `entrees` | https://entrees.es/busqueda/gran-canaria | ✅ Accesible | Entradas Anexo Estadio Gran Canaria   entrées.es | a[href*="/evento/"]:798, a[href*="/entradas/"]:56, h2:230, h3:270, [class*="title"]:254, [class*="price"]:0 |
| `institucional:cicca` | https://www.fundacionlacajadecanarias.es/agenda-cultural/ | ✅ Accesible | Agenda Cultural - Fundación La Caja de Canarias | article:22, article a:66, article h2:0, article h3:0 |
| `institucional:guiniguada` | https://www3.gobiernodecanarias.org/cultura/ocio/teatroguiniguada/eventos/ | ✅ Accesible | Eventos - Teatro Guiniguada | a[href*="/eventos/"]:24, article:8, h2:0, h3:1 |
| `telde_cultura` | https://teldecultura.org/ | ✅ Accesible | Telde Cultura – Tu espacio cultural en el Municipio de Telde | article:1, .event-card:0, .card:12, .evento:0, div[class*="event"]:71, div[class*="actividad"]:0, a[href]:177 |
| `ticketmaster_web` | https://www.ticketmaster.es/search?q=gran%20canaria | ⚠️ Bloqueado |  | [data-testid="event-list-item"]:0, .event-listing__item:0, a[href*="/event/"]:0, a[href*="/activity/"]:0 |
| `tickety` | https://tickety.es/search/gran%20canaria | ✅ Accesible | Tickety | a[href*="/event/"]:12, img:17, [class*="price"]:12 |
| `tomaticket` | https://www.tomaticket.es/es-es/gran-canaria | ✅ Accesible | Tomaticket.es - Venta de entradas, tickets y gestión de eventos > Gran Canaria | a.eventtt:140, h2:398, .fecha:140, img:205 |

### 1.7 Evidencia puntual de bloqueos anti-bot (Playwright)

#### https://entrees.es/busqueda/gran-canaria
- title: `Just a moment...`
- markers: just_a_moment=False, security_verification=True, browsing_paused=False, identity_verified=False, cloudflare=True
- anchor_count: 2
- preview: `entrees.es performing security verification  this website uses a security service to protect against malicious bots. this page is displayed while the website verifies you are not a bot.  ray id: 9d44f9783d49f7ae performance and security by cloudflare privacy`

#### https://www.ticketmaster.es/search?q=gran%20canaria
- title: ``
- markers: just_a_moment=False, security_verification=False, browsing_paused=True, identity_verified=False, cloudflare=False
- anchor_count: 2
- preview: `your browsing activity has been paused we've detected unusual behavior on either your network or your browser.  to resolve this:  sign in to your account if you haven't already change your wi-fi or cellular network switch devices or move to a different location if possible 46.225.64.147 08aec683-6b78-4549-a411-c97b15dbe4c0 we and our partners proce`

#### https://www.entradas.com/search/?affiliate=EES&searchterm=Gran+canaria
- Error: `Page.goto: net::ERR_HTTP2_PROTOCOL_ERROR at https://www.entradas.com/search/?affiliate=EES&searchterm=Gran+canaria`

### 1.8 Evidencia de endpoints/API detectados

#### Cultura Canaria (Auditorio/Pérez Galdós)
- `auditorio` endpoint: `https://auditorioalfredokraus.es/eventos/0?page=N`
  - items muestreados: 60
  - cobertura campos: title=60, start_date=60, start_time=60, price=3, tickets_url=57, space=60, room=60
  - muestra: Diana Navarro | 2026-02-28 20:00 | price=None | tickets_url=https://auditorioalfredokraus.janto.es/janto/main.php?Nivel=Evento&idEvento=DIANAN0226
- `teatro_perez_galdos` endpoint: `https://teatroperezgaldos.es/eventos/0?page=N`
  - items muestreados: 19
  - cobertura campos: title=19, start_date=19, start_time=19, price=0, tickets_url=19, space=19, room=19
  - muestra: Poliedro de amor | 2026-02-27 20:00 | price=None | tickets_url=https://teatroperezgaldos.janto.es/janto/main.php?Nivel=Evento&idEvento=POLIEAMR0226

#### EntradasCanarias API
- `entradas_canarias_current_events` -> status=200 | count=105 | url=https://12bwlcduo0.execute-api.eu-west-1.amazonaws.com/events/current-events
  - sample_keys: masterId, title, slug, url, imageUrl, city, province, venue, category, sessions, minPrice, important, hasPriority, hidden
  - sample: {'title': 'Carlitos Brownie Band ', 'slug': 'entradas-carlitos-brownie-band-las-palmas', 'url': 'https://ventas.entradascanarias.com/events/carlitos-brownie-band', 'city': 'Las Palmas', 'province': 'Las Palmas', 'venue': 'Bodega Los Lirios', 'category': 'conciertos', 'minPrice': 10, 'sessions': [{'date': '2026-03-06T20:30:00.000+00:00', 'sold': False, 'providerId': None}]}
- `entradas_canarias_slider_events` -> status=200 | count=1 | url=https://12bwlcduo0.execute-api.eu-west-1.amazonaws.com/events/slider-events
  - sample_keys: eventDate, eventUrl, imageUrl, eventLocation, position, id, eventTitle, dateVisibleUntil
  - sample: {'eventTitle': 'Saul Romero - Estreno del nuevo Show FANTASÍA', 'eventDate': '15  de Marzo 19:00H', 'eventUrl': 'https://entradascanarias.com/evento/entradas-saul-romero-estreno-del-nuevo-show-fantasia-las-palmas-de-gran-canaria', 'eventLocation': 'Palacio de Congresos de Infecar'}

### 1.9 Evidencia en código (líneas clave)

#### `app/main.py`
- línea ~200: Construye _titulo_norm
- línea ~201: Marca _es_generico por lugar
- línea ~209: drop_duplicates por ["_titulo_norm", "fecha_iso"] (clave insuficiente)

#### `app/scrapers/entrees.py`
- línea ~78: Selector amplio: a[href*="/evento/"] y a[href*="/entradas/"]
- línea ~93: Fallback: nombre = línea más larga (lines.reduce)
- línea ~204: Prioriza detalle["nombre_deep"] sin validación de generic title

#### `app/scrapers/_enrichment.py`
- línea ~80: _detectar_dominio no contempla explícitamente entrees/entradas_canarias/entradas.com/telde
- línea ~628: Asigna nombre_deep desde h1 sin filtro semántico
- línea ~447: price_selectors por dominio (faltan algunos dominios explícitos)

#### `app/scrapers/institucional.py`
- línea ~29: cards = query_selector_all("article") en CICCA
- línea ~38: Título en CICCA se busca con h2/h3 (DOM real usa h4.entry-title)

#### `app/scrapers/entradas_canarias.py`
- línea ~137: seen.has(nombre): dedupe prematuro por nombre
- línea ~229: Fallback url_full a homepage si no hay URL evento

#### `app/scrapers/tickety.py`
- línea ~79: Persistencia con nombre=raw["nombre"] (no usa nombre_deep)

#### `app/scrapers/cultura_canaria.py`
- línea ~36: Scrapea DOM /programacion en lugar de endpoint JSON /eventos/0?page=N
- línea ~88: Persistencia con nombre=raw["nombre"]

#### `app/crud.py`
- línea ~35: Rama if existente en upsert (revisar actualización completa de campos, incluido lugar)
- línea ~30: hash_id por organiza|url|fecha|hora (normalizar componentes)

#### `scripts/excel_to_supabase.py`
- línea ~23: Depende de _ver_mapa para lat/lon sin guardas fuertes
- línea ~54: fecha_iso se corta por string slicing (validación mejorable)

---

## 2) DIAGNÓSTICO TÉCNICO (root cause)

### 2.1 Hallazgo principal
- El pipeline no falla por “falta de scraping” sino por combinación de:
  1) extracción frágil de título en fuentes con anti-bot/dinámicas,
  2) ausencia de guardas semánticas (generic titles) en puntos críticos,
  3) deduplicación final con clave incompleta.

### 2.2 Causas raíz por capa

#### Capa Scraping
- `entrees.py`: selector amplio + fallback “texto más largo” -> propenso a strings genéricos.
- `entradas_canarias.py`: parseo DOM de SPA cuando existe API estable; dedupe prematuro por nombre.
- `entradas_com.py`: bloqueos HTTP2/timeouts en datacenter.
- `ticketmaster_web.py`: challenge anti-bot persistente; fuente no fiable en VPS sin estrategia adicional.
- `institucional.py`: selectores CICCA no alineados con DOM real (`h4` vs `h2/h3`).
- `tickety.py`: no usa `nombre_deep` al persistir.

#### Capa Enrichment
- `_enrichment.py`: `nombre_deep` asignado desde `h1` sin filtro anti-genérico.
- `_detectar_dominio()` incompleto para varios dominios clave, forzando selectores genéricos.

#### Capa Sanitización / Export
- `main.py`: no existe QA gate hard-fail por porcentaje de títulos genéricos.
- `main.py`: dedupe por `titulo+fecha` insuficiente; puede fusionar eventos distintos del mismo día.

#### Capa Persistencia
- `crud.py`: revisar rama update para garantizar actualización coherente de campos clave (incluido lugar).
- Hash ID estable requiere normalización estricta de hora/fecha/url.

### 2.3 Impacto en calidad de datos
- Salida limpia nueva aparentemente “más limpia” visualmente (menos truncados), pero semánticamente peor por 52.4% de títulos genéricos.
- El descenso de duplicados en limpio nuevo es artificial: colapsan al mismo título basura.
- Cobertura de precio/hora sigue débil en varias fuentes (especialmente Tickety y Tomaticket hora).

### 2.4 Diagnóstico por severidad
- **P0 (bloqueante):** `entrees.py`, `_enrichment.py`, `main.py` QA gate.
- **P1 (alta):** dedupe clave compuesta, migrar EntradasCanarias a API, robustecer institucional/tickety/tomaticket, ticketmaster_web fallback.
- **P2 (media):** hardening en `crud.py` y script Excel→Supabase.

---

## 3) PLAN DE EJECUCIÓN PASO A PASO (sin resumen)

## Fase 0 — Preparación (día 0)
1. Crear rama: `fix/scraping-quality-hardening`
2. Congelar baseline (guardar excels y métricas actuales).
3. Activar logging por scraper (count total, count valid, count blocked).
4. Definir archivo de configuración central para umbrales QA.

## Fase 1 — Bloque P0 (día 1, obligatorio)

### Paso 1: `app/scrapers/entrees.py`
- Añadir `GENERIC_TITLES` + `es_titulo_generico()`.
- Detectar challenge en body y devolver `[]` limpiamente.
- Reordenar pipeline de título: `nombre_deep -> raw.nombre -> inferir_nombre(url)` con validación en cada paso.
- Restringir selectores de card real y exigir mínimo de calidad (`url + nombre + fecha|lugar`).

### Paso 2: `app/scrapers/_enrichment.py`
- Validar `h1` antes de asignar `nombre_deep` (bloquear genéricos).
- Ampliar `_detectar_dominio()` para `entrees`, `entradascanarias`, `entradas.com`, `teldecultura`.
- Añadir selectores específicos de precio/fecha/hora por nuevos dominios.

### Paso 3: `app/main.py`
- Insertar QA gate hard-fail por `% generic titles > 5%`.
- Excluir genéricos antes de export aunque no supere hard fail (limpieza preventiva).

### Verificación Fase 1
- Ejecutar pipeline completo en staging.
- Confirmar en salida: generic titles == 0 (o <1%).
- Confirmar que corrida no rompe cuando Entrees/Entradas/Ticketmaster web bloquean.

## Fase 2 — Bloque P1 (días 2–3)

### Paso 4: Dedupe robusto (`app/main.py`)
- Cambiar clave de dedupe a: `titulo_norm + fecha_iso + venue_norm + hora_norm`.
- Mantener priorización por lugar específico + descripción más completa (ya existente).

### Paso 5: `app/cleaner.py`
- Elevar umbral fuzzy (>=90).
- Agrupar por `(fecha_iso, hora_hhmm, lugar_norm)`.
- Excluir títulos genéricos del clustering fuzzy.

### Paso 6: `app/scrapers/cultura_canaria.py`
- Migrar fase listado a endpoint JSON `/eventos/0?page=N`.
- Mantener enrichment para descripción/imagen/hora fallback y precio vía Janto (`tickets_url`).
- Persistir `nombre = nombre_deep or title`.

### Paso 7: `app/scrapers/entradas_canarias.py`
- Sustituir scraping DOM principal por API `current-events` + `slider-events`.
- Filtro geográfico por `province/city/venue` normalizado.
- Dedupe interno por `slug + session.date + venue` (NO por nombre).
- No persistir homepage como URL de evento.

### Paso 8: `app/scrapers/institucional.py`
- CICCA: usar `article.et_pb_post`, `h4.entry-title`, `h4.entry-title a`.
- Guiniguada: dedupe por URL y descartar entradas “COMPRAR” como título.

### Paso 9: `app/scrapers/tickety.py`
- Persistir `nombre_deep` cuando exista.
- Añadir retry/backoff ante `ERR_HTTP2_PROTOCOL_ERROR`.

### Paso 10: `app/scrapers/tomaticket.py`
- Reemplazar scroll fijo por scroll dinámico hasta estabilización de `a.eventtt`.
- Mantener dedupe por URL al construir `eventos_raw`.

### Paso 11: `app/scrapers/telde_cultura.py`
- Base de extracción por `a[href*="/events/"]` + dedupe URL.
- Si no hay URL individual válida, descartar registro.
- Corregir warning de escape regex en JS embebido (`\d` o string raw).

### Paso 12: `app/scrapers/ticketmaster_web.py` / `ticketmaster_api.py`
- Definir `ticketmaster_api.py` como primario.
- `ticketmaster_web.py` solo fallback con detector de bloqueo y retorno limpio.

## Fase 3 — Bloque P2 (día 4)

### Paso 13: `app/crud.py`
- Revisar rama `if existente` y garantizar update de `lugar` y demás campos relevantes.
- Normalizar componentes de hash (`fecha`, `hora[:5]`, `url` strip) para estabilidad.

### Paso 14: `scripts/excel_to_supabase.py`
- Validar columnas requeridas al inicio.
- Manejar ausencia de `Ver en Mapa` sin crash (lat/lon null).
- Validar `fecha_iso` con regex estricta y log de descartes.

## Fase 4 — Testing automatizado (día 5)
1. `test_generic_title_filter.py`
2. `test_enrichment_domain_router.py`
3. `test_main_dedupe_key.py`
4. `test_challenge_detection.py`
5. `test_crud_hash_stability.py`
6. `test_scraper_contract.py` (si bloqueo -> `[]`, no excepción global)

## Fase 5 — Validación funcional (día 6)
- Ejecutar 3 corridas en staging (mañana/tarde/noche).
- Auditar métricas por corrida y comparar con baseline.
- Spot-check manual de 20 eventos aleatorios en limpio final.

## Fase 6 — Paso a producción controlado (día 7)
- Deploy con feature flags por fuente conflictiva (Entradas, Entrees, Ticketmaster web).
- Monitorear 7 corridas consecutivas.
- Si falla QA gate en producción, conservar última versión limpia válida + alertar equipo.

## 3.1 Criterios de aceptación obligatorios (DoD)
- `% títulos genéricos` < 1% (ideal 0%).
- `% hora vacía` <= 7%.
- `% precio vacío` <= 12%.
- Sin colapso artificial de duplicados por título basura.
- 7 corridas consecutivas cumpliendo métricas y sin ruptura global del pipeline.

## 3.2 Política anti-bot operativa
- Fuentes bloqueables deben tener `challenge detector + retries + fallback + return []` limpio.
- No bloquear el pipeline por una sola fuente.
- Registrar estado por fuente: `ok | blocked | timeout | empty` + timestamp.

## 3.3 Entregables para tu equipo técnico
1. PR único o PRs por módulo (P0/P1/P2).
2. `CHANGELOG_scraping.md` con cambios y fecha.
3. `metrics_run_YYYYMMDD.json` por ejecución.
4. Script de auditoría post-run (`scripts/audit_export.py`).
5. Evidencia de tests (pytest + cobertura mínima acordada).

---

## 4) APÉNDICE A — Documentos analizados

 `app/main.py` 
 `app/scrapers/tomaticket.py` 
 `app/scrapers/cultura_canaria.py` 
 `app/scrapers/entradas_canarias.py` 
 `app/scrapers/entradas_com.py` 
 `app/scrapers/entrees.py` 
 `app/scrapers/institucional.py` 
 `app/scrapers/telde_cultura.py` 
 `app/scrapers/ticketmaster_api.py` 
 `app/scrapers/ticketmaster_web.py` 
 `app/scrapers/tickety.py` 
 `app/auditor.py` 
 `app/classifier.py` 
 `app/cleaner.py` 
 `app/enricher.py` 
 `app/geocoder.py` 
 `app/scrapers/_enrichment.py` 
 `app/database.py` 
 `app/models.py` 
 `app/crud.py` 
 `scripts/excel_to_supabase.py` 

## 5) APÉNDICE B — Archivos de evidencia generados

- `Audit/evidencia_excels_scraping_full.json`
- `Audit/evidencia_webs_scraping_full.json`
- `Audit/evidencia_bloqueos_playwright.json`
- `Audit/evidencia_endpoints_fuentes_full.json`

Estos JSON contienen el detalle bruto reproducible del análisis.