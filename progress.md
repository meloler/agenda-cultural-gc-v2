# Progress

## Current State

Branch: `rebuild/product-harness-v0`.

This is a controlled restart from `main`, not a full deletion. The old static frontend has been isolated in `legacy/frontend-static/` for reference. The `scrapers/` pipeline remains untouched and must be preserved.

## Files Created Or Updated In Previous Harness Task

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
- `docs/decisions/ADR-001-product-shape.md`
- `docs/decisions/ADR-002-stack.md`
- `docs/decisions/ADR-003-data-model.md`
- `docs/decisions/ADR-004-auth-personalization.md`
- `docs/decisions/ADR-005-scraping-ai-enrichment.md`
- `docs/playbooks/implement-feature.md`
- `docs/playbooks/add-api-endpoint.md`
- `docs/playbooks/add-database-table.md`
- `docs/playbooks/fix-bug.md`
- `docs/playbooks/review-pr.md`
- `docs/playbooks/run-validation.md`
- `docs/checklists/manual-qa.md`
- `docs/checklists/event-quality.md`
- `docs/checklists/privacy.md`
- `docs/plans/active/`
- `docs/plans/completed/`

## Files Moved To Legacy In This Task

Moved to `legacy/frontend-static/`:

- `index.html`
- `app.js`
- `style.css`
- `manifest.json`
- `sw.js`
- `purify.min.js`
- `mobile_cupertino_preview.html`
- `mobile_editorial_preview.html`
- `mobile_mensual.html`
- `stitch_calendar.html`
- `stitch_event_detail.html`
- `serve.json`
- `stitch_designs/`

Created:

- `legacy/frontend-static/README.md`

Updated:

- `PROJECT.md`
- `ARCHITECTURE.md`
- `progress.md`

## Files Not Moved And Why

- `scrapers/`: protected ingestion, enrichment, geolocation, sanitization and export pipeline.
- `scripts/`: may be shared build/feed/env infrastructure; not moved without a separate config decision.
- `package.json`: references old frontend assumptions but also owns root commands/dependencies; not moved without deciding new app stack.
- `package-lock.json`: paired with `package.json`.
- `vercel.json`: production/deploy configuration; not changed in this task.
- `.env.example`: environment documentation; not frontend-only.
- `README.md`, `PROJECT.md`, `PRODUCT_SPEC.md`, `ROADMAP.md`, `RISKS.md`, `SECURITY.md`, `TESTING.md`: harness/documentation.
- `ARCHITECTURE.md`: updated in place because it describes the repository.
- `scripts/generate_feeds.mjs`: generates feeds; may be reused later.
- `scripts/inject_env.mjs`: currently assumes root `index.html`; left in place and documented as pending.

## Decisions Made

- V0 is anonymous discovery only.
- V0 does not include login, persistent favorites, admin panel or behavioral personalization.
- The product shape is dynamic collections, not chronological agenda.
- `scrapers/` and existing IA enrichment are preserved.
- A future Event Intelligence layer is required before the new app consumes real event data deeply.
- The old static frontend is now legacy reference, not the base of the new app.
- Features in `feature_list.json` remain `passes:false`.

## Reviewable Assumptions

- New app will live in `apps/web/`.
- Event Intelligence implementation location is TBD — requires user decision.
- Frontend stack is TBD — requires user decision.
- Cheap-price threshold is TBD — requires user decision.
- Friday evening cutoff for weekend collections is TBD — requires user decision.
- Root build/deploy config will be updated in a later explicit task.

## Blockers

- No frontend stack decision yet.
- No formal data contract yet.
- No real frontend lint/typecheck/unit test setup yet.
- No secret scanning configured yet.
- No Event Intelligence implementation yet.
- Root `npm run build` may fail or be incomplete until `scripts/inject_env.mjs` and app entrypoint are updated for the new structure.

## Validation Run

Validation performed for legacy isolation:

- Checked candidate frontend references before moving.
- Moved only frontend-static files and prototype/design assets.
- Confirmed `scrapers/` still exists.
- Confirmed no files under `scrapers/` changed.
- Checked Git status and diff summary.

Not run:

- Frontend tests: no useful frontend test command exists yet.
- Frontend lint/typecheck: not configured yet.
- `npm run build`: intentionally not run after moving `index.html` because current build script still assumes root legacy frontend and needs a separate explicit update.
- Scraper tests: not needed for frontend file move and `scrapers/` was not touched.

## Next Recommended Task

Create the first active plan in `docs/plans/active/` for `FEAT-001 Event Intelligence`, defining publishable-event rules, scoring inputs and collection assignment rules using mock/sample data only.
