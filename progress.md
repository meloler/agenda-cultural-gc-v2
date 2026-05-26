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

Validation passed with 14 real Event Intelligence tests.

### FEAT-002: Mobile-First Mock Home

Implemented the first V0 home using mock data and Event Intelligence.

What changed:

- Replaced the placeholder page with a mobile-first discovery home.
- Added a simple product header.
- Added hero copy around: `¿Qué plan te apetece?`.
- Added an intention cloud with the required chips.
- Added horizontal collection rails.
- Added event cards showing image/placeholder, title, date, time, place, price, category, editorial signal and ranking reason.
- Added mock events covering today, weekend, free, family, music, theatre, market, hidden gem, incomplete-but-publishable and non-publishable cases.
- Added a web collection adapter that consumes Event Intelligence instead of duplicating scoring or collection logic.
- Added real `apps/web` Vitest tests for collection presentation.
- Updated root `npm test` so it runs Event Intelligence tests and web tests.

Files created or updated:

- `apps/web/app/page.tsx`
- `apps/web/app/globals.css`
- `apps/web/components/Hero.tsx`
- `apps/web/components/IntentCloud.tsx`
- `apps/web/components/EventRail.tsx`
- `apps/web/components/EventCard.tsx`
- `apps/web/lib/mock-events.ts`
- `apps/web/lib/collections.ts`
- `apps/web/lib/__tests__/collections.test.ts`
- `apps/web/package.json`
- `apps/web/next.config.ts`
- `packages/event-intelligence/package.json`
- `package.json`
- `package-lock.json`
- `PRODUCT_SPEC.md`
- `ARCHITECTURE.md`
- `TESTING.md`
- `feature_list.json`
- `progress.md`

Important boundaries respected:

- `scrapers/` unchanged.
- `legacy/frontend-static/` unchanged.
- `vercel.json` unchanged.
- No Supabase connection added.
- No login implemented.
- No persistent favorites implemented.
- No personalization implemented.
- No production connection added.
- No secrets added.

## FEAT-002 Decisions

- The V0 home uses mock data only.
- The visual direction is warm editorial/island culture rather than generic dashboard UI.
- Collections are generated in `apps/web/lib/collections.ts` using Event Intelligence.
- `apps/web/next.config.ts` transpiles `@agenda-cultural-gc/event-intelligence` so Next can consume the local workspace package.
- Component tests are deferred; current tests cover the presentation logic that decides what appears in the home.

Assumptions — to be validated:

- Mock image URLs are acceptable for V0 visual review and are not production data.
- The intention chips are visual/non-persistent in FEAT-002; filtering behavior is future scope.
- Friday evening is documented in product spec, but Event Intelligence weekend logic still uses Saturday/Sunday until the scoring rule is explicitly changed.

## Validation Run

Commands executed for FEAT-002:

- `npm install` — passed; still reports 3 moderate vulnerabilities.
- `npm run typecheck` — passed.
- `npm run lint` — passed with one non-blocking Next image warning for mock images.
- `npm test` — passed, 19 tests total.
- `npm run build` — passed.
- `npm run validate` — passed.\n- Local preview check at `http://localhost:3100` — passed: HTTP 200, hero text and collection text found.

Additional checks:

- No files under `scrapers/` changed.
- No files under `legacy/frontend-static/` changed.
- `vercel.json` unchanged.

## Risks / Blockers

- 3 moderate npm audit findings remain open and documented in `RISKS.md`.
- CI still needs to be updated for the workspace structure in a later explicit task.
- `vercel.json` still needs a separate explicit review for `apps/web`.
- Mock UI is not connected to real data yet.
- Event detail page is still future scope.
- Component/browser-level tests are not configured yet.

## Next Recommended Task

Run a visual review of the FEAT-002 home locally, then implement FEAT-004 or a small FEAT-002 polish pass before connecting any real data.
