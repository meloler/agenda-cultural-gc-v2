# Progress

## Current State

Branch: `rebuild/product-harness-v0`.

This is a controlled restart from `main`, not a full deletion. The old static frontend is isolated in `legacy/frontend-static/` for reference. The new minimal web app shell now exists in `apps/web/`. The `scrapers/` pipeline remains untouched and must be preserved.

## Previous Completed Steps

### Product Harness

Created the project harness:

- `PROJECT.md`
- `PRODUCT_SPEC.md`
- `ARCHITECTURE.md`
- `AGENTS.md`
- `ROADMAP.md`
- `RISKS.md`
- `SECURITY.md`
- `TESTING.md`
- `feature_list.json`
- `progress.md`
- `init.sh`
- ADRs, playbooks, checklists and plan folders under `docs/`.

### Legacy Frontend Isolation

Moved the old static frontend to `legacy/frontend-static/`:

- `index.html`
- `app.js`
- `style.css`
- `manifest.json`
- `sw.js`
- `purify.min.js`
- old mobile prototypes
- Stitch design artifacts

Created `legacy/frontend-static/README.md`.

## Current Task: Minimal apps/web Scaffold

Created a minimal Next.js + TypeScript app in `apps/web/`.

Created/updated:

- `package.json`
- `package-lock.json`
- `.gitignore`
- `apps/web/package.json`
- `apps/web/next.config.ts`
- `apps/web/eslint.config.mjs`
- `apps/web/tsconfig.json`
- `apps/web/next-env.d.ts`
- `apps/web/app/layout.tsx`
- `apps/web/app/page.tsx`
- `apps/web/app/globals.css`
- `packages/event-intelligence/README.md`
- `docs/decisions/ADR-002-stack.md`
- `ARCHITECTURE.md`
- `TESTING.md`
- `AGENTS.md`
- `progress.md`

## Decisions Made

- Stack provisional: `apps/web` with Next.js + TypeScript.
- Root repo uses npm workspaces.
- `packages/event-intelligence/` is reserved as a placeholder only.
- The initial app page is a minimal placeholder.
- No FEAT-001 implementation was started.
- No Supabase connection was added.
- No login or personalization was added.
- `scrapers/` was not changed.
- `vercel.json` was not changed in this task.
- `node_modules/` and Next build outputs were added to `.gitignore` to avoid committing generated install/build artifacts.

## Assumptions — To Be Validated

- Next.js + TypeScript is the right stack for V0.
- New app remains in `apps/web/`.
- Event Intelligence will live in `packages/event-intelligence/`.
- Vercel should later be configured explicitly for the monorepo/new app.

## Current Root Scripts

- `npm install`
- `npm run dev`
- `npm run typecheck`
- `npm run lint`
- `npm run build`
- `npm test`
- `npm run validate`

## Validation Run

Commands executed:

- `npm install` — passed.
- `npm run typecheck` — passed.
- `npm run lint` — initially failed due ESLint flat-config/Next config issue; config was corrected; passed.
- `npm run build` — initially failed due BOM encoding in `apps/web/package.json` and `apps/web/tsconfig.json`; encoding was corrected; passed.
- `npm test` — passed as placeholder, prints that no tests are configured yet.
- `npm run validate` — passed: typecheck, lint, build and placeholder test.

Additional checks:

- `feature_list.json` remains unchanged with all features `passes:false`.
- No files under `scrapers/` changed.

## Risks / Blockers

- `vercel.json` still points to the old root static frontend flow. It was intentionally not changed to avoid accidental deployment/config breakage.
- CI still needs to be updated for the new workspace structure.
- `npm test` is only a placeholder; real tests are still pending.
- `npm install` reported 3 moderate vulnerabilities. No automatic `npm audit fix` was run because it may change dependency versions outside this task scope.
- `node_modules/` contains generated local install artifacts and is intentionally ignored for new files. Existing tracked historical `node_modules` content remains a separate cleanup risk.
- No Event Intelligence implementation exists yet.
- No Supabase data contract exists yet.

## Next Recommended Task

Update CI and deployment harness for the new workspace without deploying production: make CI run `npm run validate`, keep scraper checks separate, and document the required Vercel project-root/build setting for `apps/web`.

