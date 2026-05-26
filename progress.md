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

### FEAT-006: Preparation For Registered User And Explicit Preferences

V1/V2 personalization architecture and privacy framework documented without implementing
login, favorites, tracking or any functional change.

What changed:

- Expanded `docs/decisions/ADR-004-auth-personalization.md` with full status, context,
  V0/V1/V2 decision, auth provider recommendation, alternatives, consequences, risks,
  activation signals and related documents.
- Created `docs/plans/active/user-personalization-v1.md` with V1/V2 product scope,
  conceptual data model (user_profile, user_interest, saved_event, event_feedback,
  personalization_consent) and implementation conditions.
- Created `docs/checklists/auth-readiness.md` with conditions required before activating
  V1 auth: architecture, migrations, RLS, auth flow, V0 preservation.
- Created `docs/checklists/personalization-readiness.md` with conditions required before
  activating V1 personalization: consent, preference scope, recommendation logic,
  security, testing, V2 gate.
- Expanded `docs/checklists/privacy.md` with detailed V0/V1/V2 sections and general rules.
- Added V1/V2 roadmap section to `PRODUCT_SPEC.md`.
- Added Future Auth And Personalization Architecture section to `ARCHITECTURE.md`
  (V0/V1/V2 separation, conceptual entities, RLS rules, frontend constraints,
  activation gate).
- Expanded `SECURITY.md` V1/V2 Personal Data section with V1-specific rules,
  V2-specific rules and activation gate.
- Added "Required Sensors Before V1 Auth Implementation" section to `TESTING.md`
  (auth flow, RLS/tenant isolation, personal data controls, consent gate, V0
  preservation, security — all defined but not yet implemented).
- Added risks R10–R15 to `RISKS.md`: personal data exposure, RLS misconfiguration,
  behavioral tracking without consent, opaque recommendations, forced login, premature
  personalization.
- Created `apps/web/lib/user-preferences/types.ts` with conceptual TypeScript interfaces
  for UserProfile, UserInterest, SavedEvent, EventFeedback and PersonalizationConsent.
  Not imported by any V0 page or component. Clearly marked as conceptual/future.
- Marked FEAT-006 as `passes: true` in `feature_list.json`.

Decisions made:

- Recommended auth provider: Supabase Auth (consistent with existing stack).
- Registration is always optional — V0 must work fully without account.
- V1 is explicit preferences only; no implicit behavioral signals.
- V2 is a separate future feature requiring opt-in consent per signal type.
- `behavioral_personalization_enabled` defaults to `false` and requires V2 activation.
- No login is implemented; this task is documentation and preparation only.

Files created:

- `docs/plans/active/user-personalization-v1.md`
- `docs/checklists/auth-readiness.md`
- `docs/checklists/personalization-readiness.md`
- `apps/web/lib/user-preferences/types.ts`

Files updated:

- `docs/decisions/ADR-004-auth-personalization.md`
- `docs/checklists/privacy.md`
- `PRODUCT_SPEC.md`
- `ARCHITECTURE.md`
- `SECURITY.md`
- `TESTING.md`
- `RISKS.md`
- `feature_list.json`
- `progress.md`

Important boundaries respected:

- `scrapers/` unchanged.
- `legacy/frontend-static/` unchanged.
- `vercel.json` unchanged.
- No login implemented.
- No favorites implemented.
- No tracking implemented.
- No personalization activated.
- No Supabase migrations created.
- No production connection.
- No secrets added.
- No service role key used.
- `apps/web/lib/user-preferences/types.ts` is not imported by any V0 page or component.

Assumptions — to be validated:

- Supabase Auth remains the preferred provider. Revisit if the stack changes.
- V1 budget preference taxonomy ("free", "low", "any") is a placeholder.
- V1 interest tags taxonomy is not yet defined; editorial input needed.
- V1 municipality list for Gran Canaria is not yet defined.

## FEAT-006 Validation Run

Commands executed:

- `npm run typecheck` — passed.
- `npm run lint` — passed with two non-blocking Next image warnings (pre-existing).
- `npm run build` — passed.
- `npm test` — passed, 41 tests total (14 event-intelligence + 27 apps/web).
- `npm run validate` — passed.

Additional checks:

- No files under `scrapers/` changed.
- No files under `legacy/frontend-static/` changed.
- `vercel.json` unchanged.
- No V0 component imports `apps/web/lib/user-preferences/types.ts`.

## Risks / Blockers

- 3 moderate npm audit findings remain open (pre-existing, documented in RISKS.md R8).
- CI still needs to be updated for the workspace structure.
- `vercel.json` still needs a separate explicit review for `apps/web`.
- V1 auth requires a new dedicated feature with RLS, migrations and privacy review.
- V1 preference taxonomy (interests, municipalities, budget labels) needs editorial input.

## Next Recommended Task

Deploy V0 to a staging environment, or run the manual mobile QA checklist at 375px on
real data before deciding whether to start V1 auth/personalization implementation.
V1 implementation should start only after `docs/checklists/auth-readiness.md` and
`docs/checklists/personalization-readiness.md` are ready to be checked.
