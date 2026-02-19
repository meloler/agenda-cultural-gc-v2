# 🎭 Agenda Cultural de Gran Canaria v5.1

![Canarias](https://img.shields.io/badge/Region-Gran%20Canaria-blue?style=for-the-badge&logoColor=white)
![Python](https://img.shields.io/badge/python-3.10+-yellow?style=for-the-badge&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Scraper-Playwright-green?style=for-the-badge&logo=playwright&logoColor=white)
![IA](https://img.shields.io/badge/AI-Enrichment-blueviolet?style=for-the-badge&logo=openai&logoColor=white)

> **Pipeline de precisión para la recopilación, auditoría y geolocalización de eventos culturales en la isla de Gran Canaria.**

Este proyecto automatiza la extracción de datos desde las principales plataformas de ticketing y cultura (Ticketmaster, Tomaticket, Tickety, Auditorio Alfredo Kraus, etc.), aplicando una **Auditoría Detective (Deep Scrape)** para garantizar que cada evento tenga una ubicación precisa y datos geolocalizados listos para su visualización.

---

## 🛠️ El Pipeline de Precisión (v5.1)

El sistema sigue un flujo optimizado en 8 pasos:

1.  **Scraping**: Extracción paralela distribuida usando Playwright.
2.  **Limpieza Cross-Fuente**: Eliminación de duplicados y normalización de textos.
3.  **Auditoría Detective (v2)**: 
    *   Si un evento tiene lugar "Gran Canaria" (genérico), el sistema visita la URL original.
    *   Extrae el recinto real del DOM (ej: Sala Scala, Teatro Cuyás).
    *   Capacidad de inferencia mediante IA si el scraping directo falla.
4.  **Clasificación Inteligente**: Categorización de eventos (Música, Teatro, Familia, etc.).
5.  **Enriquecimiento IA**: Extracción de descripciones, precios reales y validación de imágenes.
6.  **Geolocalización (GIS)**: Conversión de lugares a coordenadas exactas (Lat/Lon).
7.  **Sanitización Final**: Filtrado de títulos basura y precios absurdos (>300€).
8.  **Excel Export**: Generación de reportes limpios y organizados para consumo final.

---

## ✨ Características Principales

-   🚀 **Deep Scraping**: No más lugares genéricos. Si la fuente dice "Gran Canaria", el auditor encuentra el recinto exacto.
-   📍 **Auto-Geocoding**: Generación automática de enlaces a **Google Maps** con coordenadas precisas.
-   💰 **Control de Precios**: Algoritmo que identifica errores de parser (ej: confundir el año 2025 con el precio).
-   🧹 **Deduplicación Inteligente**: Si un evento aparece en varias webs, se mantiene la versión con la descripción más rica y el lugar más específico.

---

## 🚀 Instalación y Uso

1.  Clona el repositorio:
    ```bash
    git clone https://github.com/meloler/agenda-cultural-gc-v2.git
    ```
2.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```
3.  Configura tus variables de entorno en un archivo `.env` (usa `.env.example` como guía).
4.  Ejecuta el pipeline:
    ```bash
    python main.py
    ```

---

## 📊 Salida de Datos

El sistema genera dos archivos Excel:
-   `agenda_cultural_LIMPIA.xlsx`: Eventos con fecha confirmada y geolocalizados.
-   `agenda_cultural_BORRADORES.xlsx`: Eventos que requieren revisión manual o faltan datos.

---

## 📝 Autor

**Juan Salán Vila (meloler)** - *Consultor de Operaciones & Gemelo Digital*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/juansalan)
[![Github](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/meloler)
