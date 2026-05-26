# Product Spec

## One-Line Definition

Agenda Cultural GC is a mobile-first plan discovery guide for Gran Canaria, organized by dynamic intent-based collections instead of a chronological agenda.

## Product Goal

Help people decide what to do quickly, especially on mobile, using curated and explainable event collections.

## Target Experience

A user opens the app and sees collections like:

- Top planes de hoy.
- Este finde.
- Gratis o baratos.
- Con niños.
- Música en directo.
- Teatro y escena.
- Mercadillos y ferias.
- Joyas escondidas.

The user should not need to understand event sources, scraping, categories or database structure.

## MVP V0

### Included

- Anonymous mobile-first home.
- Intention cloud.
- Dynamic collections.
- Simple auditable ranking.
- Event card.
- Event detail page.
- Clear reason why an event appears in a collection.
- Mock-data support for early UI development.

### Home V0 Shape

The first home experience is a mobile-first discovery surface, not a calendar.

It contains:

- A simple header with the product name and a short discovery promise.
- A hero asking: "¿Qué plan te apetece?"
- An intention cloud with quick prompts such as Hoy, Este finde, Gratis, Con niños, Música and Teatro.
- Horizontal collection rails generated from Event Intelligence.
- Event cards focused on fast decisions: what, when, where, price, category and why it appears.

Current FEAT-002 data is mock-only and clearly marked as demo content.

### Excluded

- Login.
- Persistent favorites.
- Behavioral personalization.
- Admin panel.
- Push notifications.
- Payments.

## Collection Definitions

### Top planes de hoy

Events happening today, ranked by freshness, quality and relevance.

### Este finde

Friday evening through Sunday. Exact cutoff TBD — requires user decision.

### Gratis o baratos

Free events or low-price events. Cheap threshold TBD — requires user decision.

### Con niños

Family-friendly events based on category, keywords, source metadata and venue context.

### Música en directo

Concerts, live music, jams and music events.

### Teatro y escena

Theater, dance, performance, comedy and stage events.

### Mercadillos y ferias

Markets, fairs, artisan, gastro and local product events.

### Joyas escondidas

Smaller or less obvious events with good quality signals and lower mainstream visibility. Exact ranking formula TBD — requires user decision.

## Ranking Principles

Ranking must be simple and explainable in V0.

Possible scoring inputs:

- Is the event soon?
- Is the date reliable?
- Is the place clear?
- Is there an image?
- Is there a useful description?
- Is there a price or clear free signal?
- Is it relevant for the current collection?
- Is the source trusted?

## Success Criteria V0

- A user can understand what to do today or this weekend without opening filters.
- Event cards are decision-oriented, not database-oriented.
- Every collection can explain why an event is there.
- The app works well on mobile first.
- The pipeline remains intact.
