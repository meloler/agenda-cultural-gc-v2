# Progress

## Current State

Branch: `rebuild/product-harness-v0`.

This is a controlled restart from `main`, not a full deletion. The old static frontend is isolated in `legacy/frontend-static/` for reference. The new minimal web app shell exists in `apps/web/`. The `scrapers/` pipeline remains untouched and must be preserved.

## Previous Completed Steps

### Product Harness

Created the project harness docs, ADRs, playbooks, checklists and plan folders.

### Legacy Frontend Isolation

Moved the old static frontend to `legacy/frontend-static/` and documented it as reference only.

### Minimal apps/web Scaffold

Created a minimal Next.js + TypeScript app in `apps/web/`, npm workspace scripts, and `packages/event-intelligence/` placeholder.

## Current Task: Repository Hygiene Before FEAT-001

Performed safe repo hygiene before implementing Event Intelligence.

Changes made:

- Confirmed `node_modules/` was tracked by Git from the old repo state.
- Removed `node_modules/` from the Git index with `git rm -r --cached node_modules`.
- Kept local dependencies installed; files were removed from tracking, not from local working dependencies.
- Confirmed no tracked generated artifacts remain for patterns: `node_modules/`, `.next/`, `dist/`, `build/`, `coverage/`, `.log`, `.tmp`, `.cache/`, `.tsbuildinfo`.
- Confirmed `.gitignore` covers `node_modules/`, nested `node_modules/`, `.next/`, nested `.next/`, `dist/`, `out/` and `*.tsbuildinfo`.
- Documented npm audit risk in `RISKS.md`.

Files updated:

- `.gitignore`
- `RISKS.md`
- `progress.md`

Index-only cleanup:

- `node_modules/` removed from Git tracking.

## npm Audit Result

Command:

```bash
npm audit --json
```

Result: 3 moderate vulnerabilities.

Details:

- `postcss` `<8.5.10`: moderate XSS advisory `GHSA-qx2v-qp2m-jg93`, transitive through `next`.
- `next`: moderate because it depends on the affected `postcss` range reported by npm audit.
- `ws` `>=8.0.0 <8.20.1`: moderate uninitialized memory disclosure advisory `GHSA-58qx-3vcg-4xpx`, transitive.

Action taken:

- No automatic fix applied.
- No `npm audit fix --force` run.
- Risk documented for follow-up before production deployment.

## Validation Run

Commands executed:

- `npm install` — passed; still reports 3 moderate vulnerabilities.
- `npm run validate` — passed.

`npm run validate` executed:

- `npm run typecheck` — passed.
- `npm run lint` — passed.
- `npm run build` — passed.
- `npm test` — passed as placeholder, prints that no tests are configured yet.

Additional checks:

- `feature_list.json` remains unchanged with all features `passes:false`.
- No files under `scrapers/` changed.
- `vercel.json` unchanged.

## Risks / Blockers

- 3 moderate npm audit findings remain open.
- `npm test` is still only a placeholder.
- CI still needs to be updated for the workspace structure.
- `vercel.json` still needs a separate explicit review for `apps/web`.
- No Event Intelligence implementation exists yet.
- No Supabase data contract exists yet.

## Next Recommended Task

Update CI and deployment harness for the new workspace without deploying production: make CI run `npm run validate`, keep scraper checks separate, and document the required Vercel project-root/build setting for `apps/web`.
