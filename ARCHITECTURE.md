# Architecture

## Current Architecture

The repository currently has:

- A legacy vanilla frontend at the repository root.
- A Python ingestion pipeline in `scrapers/`.
- Supabase as event storage and frontend data source.
- Build scripts in `scripts/` for environment injection and feed generation.
- Vercel deployment configuration.

## Target Architecture For Controlled Rebuild

```text
apps/
  web/
    # future mobile-first discovery app

scrapers/
  # existing ingestion, enrichment, geolocation and export pipeline

docs/
  # decisions, playbooks, checklists and plans

scripts/
  # shared build/validation scripts

legacy/
  # current frontend after a future approved move
```

## Pipeline To Preserve

`scrapers/` remains the ingestion system:

1. Scrape events from public sources.
2. Enrich event details with existing IA pipeline where configured.
3. Classify events.
4. Audit places and locations.
5. Geolocate.
6. Sanitize.
7. Export Excel/JSON.
8. Upload curated events to Supabase.

## New Event Intelligence Layer

A new Event Intelligence layer should sit between raw/curated event data and the frontend experience.

Responsibilities:

- Validate whether an event is publishable.
- Calculate simple auditable scoring.
- Assign dynamic collections.
- Explain why an event appears in a collection.
- Provide stable data for the mobile-first app.

Implementation location TBD — requires user decision.

Potential options:

- Python module inside `scrapers/app/intelligence/`.
- Separate scripts under `scripts/event-intelligence/`.
- Frontend adapter under `apps/web/` for V0 mock/derived collections.

## Frontend Direction

The future app should live under `apps/web/`.

Stack TBD — requires user decision.

Constraints:

- Mobile-first.
- No login in V0.
- Must support mock data before production data connection.
- Must consume curated event shape, not raw scraper internals.

## Data Flow Target

```text
Public sources
  -> scrapers/
  -> enrichment/classification/geolocation/sanitization
  -> Supabase or curated event export
  -> Event Intelligence
  -> apps/web mobile discovery experience
```

## Production Safety

No production deploys, migrations, destructive data changes or secret changes without explicit approval.
