# AGENTS.md

## Read First

Before changing code, read:

1. `PROJECT.md`
2. `PRODUCT_SPEC.md`
3. `ARCHITECTURE.md`
4. `ROADMAP.md`
5. `RISKS.md`
6. `TESTING.md`
7. `progress.md`
8. Relevant ADRs in `docs/decisions/`

## Repository Shape

- New web app shell: `apps/web/`.
- Future Event Intelligence placeholder: `packages/event-intelligence/`.
- Protected scraper/enrichment pipeline: `scrapers/`.
- Legacy static frontend reference: `legacy/frontend-static/`.

## Working Rules

- Work in the current feature branch, not `main`.
- Do not deploy production without explicit approval.
- Do not commit secrets, tokens, keys or real credentials in code or docs.
- Do not edit `.env` or secret files unless explicitly instructed.
- Do not run destructive database migrations without explicit approval.
- Do not delete files during rebuild; move to `legacy/` only when approved.
- Do not break or rewrite `scrapers/` without a documented reason.
- Preserve the existing scraping and IA enrichment pipeline.
- V0 has no login, no persistent favorites and no behavioral personalization.
- Do not connect Supabase to `apps/web` until the data contract and security path are documented.
- Mark unclear decisions as `TBD — requires user decision` or `Assumption — to be validated`.

## Current Commands

Root workspace:

```bash
npm install
npm run dev
npm run typecheck
npm run lint
npm run build
npm test
npm run validate
```

Scraper validations, from `scrapers/` when scraper files change:

```bash
python -m pytest test_precision.py -v
python -m pytest tests/ -v
python scripts/qa_report.py
```

## Validation Rule

Before marking a task complete, run the relevant available validations and document what passed or could not run.

If no validation exists, say so in `progress.md` and recommend the missing sensor.

## Documentation Rule

Update `progress.md` after every task with:

- What changed.
- Decisions made.
- Files touched.
- Validations run.
- Next recommended task.

Do not mark any `feature_list.json` item as `passes:true` unless its acceptance criteria and validation are complete.
