# Progress

## Current State

Branch: `rebuild/product-harness-v0`.

This is a controlled restart from `main`, not a full deletion. The existing frontend remains in place. The `scrapers/` pipeline remains untouched and must be preserved.

## Files Created Or Updated In This Task

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

## Decisions Made

- V0 is anonymous discovery only.
- V0 does not include login, persistent favorites, admin panel or behavioral personalization.
- The product shape is dynamic collections, not chronological agenda.
- `scrapers/` and existing IA enrichment are preserved.
- A future Event Intelligence layer is required before the new app consumes real event data deeply.
- Features in `feature_list.json` are all marked `passes:false`.

## Reviewable Assumptions

- New app will live in `apps/web/`.
- Current frontend will later move to `legacy/`, but not in this task.
- Event Intelligence implementation location is TBD — requires user decision.
- Frontend stack is TBD — requires user decision.
- Cheap-price threshold is TBD — requires user decision.
- Friday evening cutoff for weekend collections is TBD — requires user decision.

## Blockers

- No frontend stack decision yet.
- No formal data contract yet.
- No real frontend lint/typecheck/unit test setup yet.
- No secret scanning configured yet.
- No Event Intelligence implementation yet.

## Validation Run

Documentation-only task. No product features were implemented.

Validation performed:

- Confirmed harness files exist.
- Confirmed `feature_list.json` parses as valid JSON.
- Confirmed no files under `scrapers/` changed.
- Checked Git status and diff summary.

Not run:

- Frontend tests: no useful frontend test command exists yet.
- Frontend lint/typecheck: not configured yet.
- Scraper tests: not needed for documentation-only changes and `scrapers/` was not touched.

## Next Recommended Task

Create the first active plan in `docs/plans/active/` for `FEAT-001 Event Intelligence`, defining publishable-event rules, scoring inputs and collection assignment rules using mock/sample data only.
