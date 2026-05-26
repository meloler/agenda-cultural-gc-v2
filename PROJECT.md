# Agenda Cultural GC — Project Harness

Agenda Cultural GC is a mobile-first discovery guide for plans in Gran Canaria.

It is not a chronological agenda. It should feel closer to Netflix or Spotify: dynamic collections, clear recommendations, and fast decision-making.

## Product Shape

The product helps a person answer: "What can I do today, this weekend, with kids, cheaply, with music, or somewhere interesting?"

Events are prioritized by:

- User intent.
- Date/time relevance.
- Data quality.
- Cultural/ocio relevance.
- Explainable scoring.

## Current Repository Role

This repository contains two important systems:

- Existing ingestion pipeline in `scrapers/`: scraping, enrichment, classification, geolocation, sanitization, export and Supabase upload.
- Legacy static frontend preserved in `legacy/frontend-static/`: previous vanilla HTML/CSS/JS SPA and design prototypes.

The restart is controlled: preserve the pipeline, keep the old frontend as reference, then build the new mobile-first web app.

## V0 Scope

V0 is anonymous discovery:

- Mobile-first home.
- Intention cloud.
- Dynamic collections.
- Simple auditable ranking.
- Event detail page optimized for fast decision.
- No login.
- No persistent favorites.
- No behavioral personalization.
- No admin panel.

## V1/V2 Direction

- V1: registered user with explicit preferences.
- V2: behavioral personalization with consent, retention and deletion controls.

## Non-Negotiables

- Do not break `scrapers/`.
- Do not expose secrets.
- Do not deploy production without explicit approval.
- Do not delete existing frontend; it is preserved in `legacy/frontend-static/` as reference only.
- Update `progress.md` after each task.
