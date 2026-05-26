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

### FEAT-005: QA Mobile, Event Quality And Link/Data Review

Implemented a quality hardening pass before adding new product functionality.

What changed:

- Added controlled loading state in `apps/web/app/loading.tsx`.
- Added controlled error state in `apps/web/app/error.tsx`.
- Added visible focus styles for links and buttons.
- Added `apps/web/lib/events/quality-report.ts` for local event quality reporting.
- Strengthened Supabase fallback messaging so production-like missing config is not silent.
- Added tests for past-event priority, empty event lists, optional missing fields, local quality report, unsafe external URL schemes, missing CTA URL and production fallback warning.
- Updated manual mobile QA checklist with concrete 375px review steps.
- Updated event quality checklist with publishable minimums, lower-quality signals, reject/review cases and Supabase contract checks.
- Documented remaining real-data QA risks.

Files created or updated:

- `apps/web/app/loading.tsx`
- `apps/web/app/error.tsx`
- `apps/web/lib/events/quality-report.ts`
- `apps/web/lib/__tests__/event-quality.test.ts`
- `apps/web/lib/events/__tests__/fallback.test.ts`
- `apps/web/components/__tests__/SafeExternalLink.test.tsx`
- `apps/web/lib/events/source.ts`
- `apps/web/lib/events/supabase.ts`
- `apps/web/app/globals.css`
- `docs/checklists/manual-qa.md`
- `docs/checklists/event-quality.md`
- `PRODUCT_SPEC.md`
- `ARCHITECTURE.md`
- `TESTING.md`
- `SECURITY.md`
- `RISKS.md`
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
- No admin panel added.
- No production deployment.
- No secrets added.
- No service role key used in `apps/web` source.

## FEAT-005 Decisions

- QA hardening stays local and testable; no external production checks were added.
- Browser/mobile QA remains a manual checklist for now.
- Link validation remains scheme-based; live HTTP link checking is future CI/QA work.
- `next/image` remains deferred until external image domains are decided.

Assumptions — to be validated:

- Manual QA at 375px will be run before any production deployment.
- Real Supabase rows need editorial sampling beyond automated publishable checks.
- The fallback mock warning is acceptable in local development when Supabase public config is absent.

## Validation Run

Commands executed for FEAT-005:

- `npm run typecheck` — passed.
- `npm run lint` — passed with two non-blocking Next image warnings for mock/external images.
- `npm test` — passed, 41 tests total.
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
- Live link/image checking is not automated yet.

## Next Recommended Task

Run the manual mobile QA checklist on the local app at 375px, then decide whether to polish visual details or move to FEAT-006 planning for future registered-user preferences without implementing login.
