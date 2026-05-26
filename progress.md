# Progress

## Current State

Branch: `rebuild/product-harness-v0`.

This is a controlled restart from `main`, not a full deletion. The old static frontend is isolated in `legacy/frontend-static/` for reference. The new web app lives in `apps/web/`. The `scrapers/` pipeline remains untouched and must be preserved.

## Completed Steps

### Product Harness

Created the project harness docs, ADRs, playbooks, checklists and plan folders.

### Legacy Frontend Isolation

Moved the old static frontend to `legacy/frontend-static/` and documented it as reference only.

### Minimal apps/web Scaffold

Created a minimal Next.js + TypeScript app in `apps/web/`, npm workspace scripts, and `packages/event-intelligence/` placeholder.

### Repository Hygiene

Removed tracked `node_modules/` from the Git index without deleting local dependencies. Confirmed generated artifacts are covered by `.gitignore`. Documented the 3 moderate npm audit findings.

### FEAT-001: Event Intelligence

Implemented `packages/event-intelligence/` as a pure TypeScript package with publishable-event validation, quality issues, deterministic scoring, MVP collection assignment and ranking explanations.

### FEAT-002: Mobile-First Mock Home

Implemented the first V0 home using mock data and Event Intelligence.

### FEAT-003: Curated Event Source / Supabase Fallback

Implemented a safe data source layer for the home, with optional public Supabase config and mock fallback.

### FEAT-004: Event Detail Page

Implemented the first event detail page optimized for fast mobile decision-making.

What changed:

- Added route `apps/web/app/events/[id]/page.tsx`.
- Added controlled not-found route state.
- Added `getEventById` using the same curated source/fallback layer from FEAT-003.
- Prevented non-publishable events from rendering as valid detail pages.
- Linked home event cards to `/events/[id]`.
- Added detail hero with image or placeholder, title, category and signal.
- Added decision panel with date, time, place, address, price, source and official CTA.
- Added recommendation reasons powered by Event Intelligence.
- Added safe external link validation for official URLs.
- Added tests for detail lookup, non-publicable events, not found, safe links, detail rendering, Event Intelligence reasons and card navigation.

Files created or updated:

- `apps/web/app/events/[id]/page.tsx`
- `apps/web/app/events/[id]/not-found.tsx`
- `apps/web/components/EventDetailHero.tsx`
- `apps/web/components/EventDecisionPanel.tsx`
- `apps/web/components/EventRecommendationReasons.tsx`
- `apps/web/components/SafeExternalLink.tsx`
- `apps/web/components/EventCard.tsx`
- `apps/web/components/__tests__/SafeExternalLink.test.tsx`
- `apps/web/components/__tests__/EventDetail.test.tsx`
- `apps/web/components/__tests__/EventCard.test.tsx`
- `apps/web/lib/events/get-event-by-id.ts`
- `apps/web/lib/events/presentation.ts`
- `apps/web/lib/events/__tests__/get-event-by-id.test.ts`
- `apps/web/app/globals.css`
- `PRODUCT_SPEC.md`
- `ARCHITECTURE.md`
- `SECURITY.md`
- `TESTING.md`
- `feature_list.json`
- `progress.md`

Important boundaries respected:

- `scrapers/` unchanged.
- `legacy/frontend-static/` unchanged.
- `vercel.json` unchanged.
- No login implemented.
- No favorites implemented.
- No personalization implemented.
- No tracking implemented.
- No production deployment.
- No secrets added.
- No service role key used in `apps/web` source.

## FEAT-004 Decisions

- Event detail uses the same event source/fallback path as the home.
- Unsafe official links are not rendered.
- No map is included in V0 detail; location remains textual for fast decision.
- Component tests use React static rendering instead of a heavier browser/component testing stack.

Assumptions — to be validated:

- `source_url` is the official destination when available.
- `lugar` can still stand in for venue/address until the real data contract is refined.
- Image optimization with `next/image` is deferred until external image domains are decided.

## Validation Run

Commands executed for FEAT-004:

- `npm run typecheck` — passed.
- `npm run lint` — passed with two non-blocking Next image warnings for mock/external images.
- `npm test` — passed, 33 tests total.
- `npm run build` — passed.
- `npm run validate` — passed.

Additional checks:

- No files under `scrapers/` changed.
- No files under `legacy/frontend-static/` changed.
- `vercel.json` unchanged.

## Risks / Blockers

- 3 moderate npm audit findings remain open and documented in `RISKS.md`.
- CI still needs to be updated for the workspace structure in a later explicit task.
- `vercel.json` still needs a separate explicit review for `apps/web`.
- Real Supabase data quality depends on RLS/public read configuration and current table contents.
- Browser-level mobile QA is still manual.

## Next Recommended Task

Run a mobile visual QA pass on the home and event detail pages, then implement FEAT-005: mobile QA, event quality and link/data review.
