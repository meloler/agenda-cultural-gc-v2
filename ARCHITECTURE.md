# Architecture

## Current Architecture

The repository currently has:

- A new minimal Next.js + TypeScript app in `apps/web/`.
- A legacy vanilla frontend preserved in `legacy/frontend-static/`.
- A Python ingestion pipeline in `scrapers/`.
- Supabase as event storage and legacy frontend data source.
- Build/feed/env scripts in `scripts/`, some of which still belong to the legacy static frontend assumptions.
- Vercel deployment configuration still pending review for the new app.

## Workspace Layout

```text
apps/
  web/
    # new mobile-first app shell, Next.js + TypeScript

packages/
  event-intelligence/
    # pure TypeScript Event Intelligence layer

scrapers/
  # existing ingestion, enrichment, geolocation and export pipeline

docs/
  # decisions, playbooks, checklists and plans

scripts/
  # legacy/shared build, feed and env scripts; review before reuse

legacy/
  frontend-static/
    # previous static frontend preserved as reference
```

## Root Scripts

The root `package.json` coordinates workspace commands:

- `npm run dev` -> `apps/web` dev server.
- `npm run build` -> builds `apps/web` and typechecks `packages/event-intelligence`.
- `npm run lint` -> lints `apps/web` and typechecks `packages/event-intelligence`.
- `npm run typecheck` -> typechecks `apps/web` and `packages/event-intelligence`.
- `npm test` -> runs real Vitest unit tests for `packages/event-intelligence`.
- `npm run validate` -> typecheck, lint, build and test.

## Legacy Frontend Status

The previous static frontend has been isolated in `legacy/frontend-static/`.

It includes the former root `index.html`, `app.js`, `style.css`, PWA files, mobile prototypes and Stitch design references.

It is not the base of the new app. It is historical reference only.

## Vercel Status

`vercel.json` was not changed in the Next.js scaffold task.

Reason: it still points to the old root `/index.html` flow, and changing deployment configuration should be a separate explicit task to avoid accidental production breakage.

Assumption — to be validated: future Vercel setup should either use `apps/web` as project root or a root monorepo configuration that builds `apps/web` safely.

## Legacy Scripts Status

`scripts/inject_env.mjs` and `scripts/generate_feeds.mjs` remain in place.

They are not deleted because they may still hold useful legacy/feed behavior, but `inject_env.mjs` no longer applies directly to the new `apps/web` shell.

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

## Event Intelligence Layer

The Event Intelligence layer sits between raw/curated event data and the frontend experience.

Location: `packages/event-intelligence/`.

Responsibilities:

- Validate whether an event is publishable.
- Calculate simple auditable scoring.
- Assign dynamic collections.
- Explain why an event appears in a collection.
- Provide stable data for the mobile-first app.

Current implementation:

- Pure TypeScript functions.
- Deterministic rules; no IA calls.
- No Supabase connection.
- No production connection.
- No secrets.
- Unit-tested with Vitest.

Public API:

- `isPublishableEvent(event)`
- `getEventQualityIssues(event)`
- `scoreEvent(event, context)`
- `assignCollections(event, context)`
- `explainEventRanking(event, context)`

Assumptions — to be validated:

- Cheap event threshold is `10` euros.
- Weekend collection currently means upcoming Saturday/Sunday from `context.now`.
- Hidden gem uses a simple quality/local-signal rule until real popularity or dedupe data exists.

## Frontend Direction

The future app lives under `apps/web/`.

Constraints:

- Mobile-first.
- No login in V0.
- Must support mock data before production data connection.
- Must consume curated event shape, not raw scraper internals.
- Must not use Supabase service role keys in frontend.

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
