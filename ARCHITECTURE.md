# Arquitectura del Proyecto

Este documento define la arquitectura general e interacciones de todo el sistema de la Agenda Cultural de Gran Canaria. Se considera la **fuente única de verdad** técnica para el proyecto.

## Diseño General Desacoplado

La plataforma funciona en dos bloques principales independientes vinculados por una base de datos central en la nube.

1. **Frontend (Vercel) -> Supabase**
   - La interfaz pública (Vanilla JS/HTML/CSS) está alojada en Vercel de forma estática.
   - La aplicación cliente lee los eventos directamente desde Supabase empleando el SDK oficial. Toda la interacción va directa a la base de datos (PostgreSQL), la cual dispone de políticas de seguridad para accesos anónimos.
   - *No existe un backend custom (API node/python)* en este paso de consulta para simplificar mantenimiento y latencias.

2. **Jobs y Scrapers -> Supabase**
   - El ecosistema de scripts en Python que hace *scraping*, enriquecimiento IA, categorización y geocodificación es el encargado exclusivo de la ingesta de datos.
   - Una vez la data está procesada, curada y geolocalizada localmente, se realiza un push directamente a las tablas de Supabase para su consumo por el Frontend.

### Estructura de Carpetas

- `root/`: Frontend estático (HTML, JS, CSS) y configuración de Vercel.
- `scrapers/`: Scripts de Python descritos en el punto 2 (Scrapers, Procesamiento e Ingesta).
- `scripts/`: Utilidades de construcción del frontend (generación de feeds, inyección de variables).

### Código Legacy

Elementos como el antiguo directorio `api/`, `deploy_backend/` y configuraciones redundantes han sido eliminados. Toda la lógica de backend reside ahora en `scrapers/` o directamente en las reglas de negocio de Supabase.
