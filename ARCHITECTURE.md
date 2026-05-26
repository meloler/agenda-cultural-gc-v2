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
    components/
      # V0 home components
    lib/
      # event source, mock data and collection presentation helpers

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

Current FEAT-002 implementation:

- `apps/web/app/page.tsx` renders the V0 mock home.
- `apps/web/components/` contains the hero, intention cloud, event rails and event cards.
- `apps/web/lib/mock-events.ts` contains clearly marked mock event data.
- `apps/web/lib/collections.ts` adapts Event Intelligence output for the home.
- The UI imports `packages/event-intelligence`; it does not duplicate scoring or collection logic.
- `apps/web/next.config.ts` uses `transpilePackages` so Next can consume the local workspace package.

Current FEAT-003 implementation:

- `apps/web/lib/events/source.ts` reads only public Supabase configuration.
- `apps/web/lib/events/supabase.ts` fetches curated future rows from the `evento` table when public config exists.
- `apps/web/lib/events/map-supabase-event.ts` maps legacy Supabase rows to the Event Intelligence event model.
- `apps/web/lib/events/get-home-events.ts` is the single data entrypoint for the home.
- If Supabase is missing, empty or unavailable, the home falls back to mock events.
- The home still filters, scores and assigns collections through Event Intelligence.

Supabase row fields currently mapped:

- `id` -> `id`
- `nombre` -> `title`
- `descripcion` -> `description`
- `fecha_iso` + `hora` -> `starts_at`
- `lugar` -> `venue_name` and `address`
- `estilo` -> `category`
- `precio_num` -> `price` / `is_free`
- `imagen_url` -> `image_url`
- `source_id` -> `source_name`
- `url_venta` -> `source_url`
- `latitud` / `longitud` -> coordinates

TBD — requires user decision: final municipality/address separation if the real Supabase table keeps only `lugar`.

Current FEAT-004 implementation:

- `apps/web/app/events/[id]/page.tsx` renders the event detail route.
- `apps/web/app/events/[id]/not-found.tsx` renders controlled not-found state.
- `apps/web/lib/events/get-event-by-id.ts` retrieves a single publishable event from the same curated source/fallback layer.
- `apps/web/components/EventDetailHero.tsx` renders image, title, category and editorial signal.
- `apps/web/components/EventDecisionPanel.tsx` renders date, time, place, price, source and official CTA.
- `apps/web/components/EventRecommendationReasons.tsx` renders Event Intelligence reasons.
- `apps/web/components/SafeExternalLink.tsx` validates external URLs before rendering links.
- Home cards link to `/events/[id]`.

External link policy:

- Only `http:` and `https:` URLs render.
- Links open in a new tab with `rel="noopener noreferrer"`.

Current FEAT-005 implementation:

- `apps/web/app/loading.tsx` provides a controlled loading state.
- `apps/web/app/error.tsx` provides a controlled error state.
- `apps/web/lib/events/quality-report.ts` provides a local event quality report utility.
- `docs/checklists/manual-qa.md` documents concrete mobile QA steps.
- `docs/checklists/event-quality.md` documents publishable-event and Supabase-contract checks.
- Additional tests cover empty inputs, optional fields, past events, fallback messaging and unsafe links.

## Data Flow Target

```text
Public sources
  -> scrapers/
  -> enrichment/classification/geolocation/sanitization
  -> Supabase or curated event export
  -> Event Intelligence
  -> apps/web mobile discovery experience
```

## Future Auth And Personalization Architecture

This section documents the planned future architecture for V1/V2. Nothing in this section
is implemented yet. Implementation requires a dedicated feature with its own checklist.

### Auth Provider

Recommended: Supabase Auth (consistent with the existing data layer).

See `docs/decisions/ADR-004-auth-personalization.md` for alternatives and rationale.

### V0 / V1 / V2 Separation

| Phase | Auth | Data | Tracking |
|-------|------|------|----------|
| V0 | Anonymous | Public events only | None |
| V1 | Optional registered user | Public events + explicit preferences | None |
| V2 | Registered user | V1 + behavioral signals | Opt-in only |

V0 must continue to work fully even after V1 is deployed. Registration is never forced.

### Conceptual Entities (V1)

No migrations exist. These define the future contract only.

- `user_profile` — explicit preferences set during onboarding.
- `user_interest` — cultural interest tags with explicit weight and source.
- `saved_event` — events saved by the user.
- `event_feedback` — like / not_interested per event.
- `personalization_consent` — consent version and per-feature opt-in flags.

See `docs/plans/active/user-personalization-v1.md` for full field definitions.

### Row Level Security

RLS must be enabled and tested on all V1 user tables before any real user data is stored.

Rules:
- Each user can read and write only their own rows.
- Unauthenticated users cannot read any V1 table.
- Service role bypass only in trusted server/pipeline contexts.

### Frontend Constraints (V1)

- `SUPABASE_SERVICE_ROLE_KEY` must never appear in `apps/web` source.
- Public anon key only in frontend.
- Privileged operations (admin, batch) only in server/pipeline contexts.
- No personal data in frontend logs or error traces.

### Activation Gate

V1 auth must not be activated until:

- `docs/checklists/auth-readiness.md` is complete.
- `docs/checklists/personalization-readiness.md` is complete.
- All required sensors in `TESTING.md` pass.
- Privacy review is completed.

## Production Safety

No production deploys, migrations, destructive data changes or secret changes without explicit approval.
