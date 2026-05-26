# Progress

## Current State

Branch: `rebuild/product-harness-v0`.

This is a controlled restart from `main`, not a full deletion. The old static frontend is isolated in `legacy/frontend-static/` for reference. The new minimal web app shell exists in `apps/web/`. The `scrapers/` pipeline remains untouched and must be preserved.

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

Implemented `packages/event-intelligence/` as a pure TypeScript package.

What changed:

- Added minimal event and context types.
- Added publishable-event validation.
- Added quality issue reporting.
- Added deterministic scoring.
- Added MVP dynamic collection assignment.
- Added ranking explanations.
- Added 14 real unit tests.
- Replaced the root placeholder `npm test` with real Event Intelligence tests.
- Updated workspace validation so `npm run validate` includes the real tests.

Files created or updated:

- `packages/event-intelligence/package.json`
- `packages/event-intelligence/tsconfig.json`
- `packages/event-intelligence/README.md`
- `packages/event-intelligence/src/types.ts`
- `packages/event-intelligence/src/quality.ts`
- `packages/event-intelligence/src/scoring.ts`
- `packages/event-intelligence/src/collections.ts`
- `packages/event-intelligence/src/index.ts`
- `packages/event-intelligence/src/__tests__/event-intelligence.test.ts`
- `package.json`
- `package-lock.json`
- `ARCHITECTURE.md`
- `TESTING.md`
- `AGENTS.md`
- `feature_list.json`
- `progress.md`

Important boundaries respected:

- `scrapers/` unchanged.
- `vercel.json` unchanged.
- No UI implemented.
- No login implemented.
- No Supabase connection added.
- No production connection added.
- No secrets added.

## FEAT-001 Decisions

- Event Intelligence is deterministic and does not use IA for V0 scoring.
- Vitest is used for fast unit testing of pure TypeScript rules.
- Cheap event threshold is `10` euros.
- Public collections exclude past events.
- Missing hour, image, price or coordinates lowers score but does not block publishing.

Assumptions — to be validated:

- Weekend collection currently means upcoming Saturday/Sunday from `context.now`.
- Hidden gems use a simple quality/local-signal rule until real popularity or dedupe signals exist.
- Duplicate penalty only uses tag-based signals until a formal duplicate field exists.

## Validation Run

Commands executed for FEAT-001:

- `npm install` — passed; still reports 3 moderate vulnerabilities.
- `npm run typecheck` — passed.
- `npm run lint` — passed.
- `npm test` — passed, 14 tests.
- `npm run build` — passed.
- `npm run validate` — passed.

Additional checks:

- No files under `scrapers/` changed.
- `vercel.json` unchanged.

## Risks / Blockers

- 3 moderate npm audit findings remain open and documented in `RISKS.md`.
- CI still needs to be updated for the workspace structure in a later explicit task.
- `vercel.json` still needs a separate explicit review for `apps/web`.
- Event Intelligence uses a minimal event model; final mapping from scraper/Supabase fields remains pending.
- Weekend definition may need product decision if Friday evening must be included in V0 collections.

## Next Recommended Task

Implement FEAT-002 with mock data only: a mobile-first home using Event Intelligence collections, without Supabase, login or production connections.
