# Testing And Validation

This file documents real commands that exist now and sensors that still need to be added.

## Current Real Commands

### Root Workspace

Install dependencies:

```bash
npm install
```

Run the new web app locally:

```bash
npm run dev
```

Build the new web app:

```bash
npm run build
```

Lint the new web app:

```bash
npm run lint
```

Typecheck the new web app:

```bash
npm run typecheck
```

Run current test command:

```bash
npm test
```

Status: this is a placeholder test command for `apps/web`. It exits successfully and prints that no tests are configured yet.

Run grouped validation:

```bash
npm run validate
```

Current `validate` runs:

1. `npm run typecheck`
2. `npm run lint`
3. `npm run build`
4. `npm test`

### apps/web

From `apps/web/` or through npm workspace:

```bash
npm run dev
npm run build
npm run lint
npm run typecheck
npm test
npm run validate
```

### Scrapers / Pipeline

From `scrapers/`:

```bash
pip install -r requirements.txt
playwright install chromium
python main.py
python upload.py
python scripts/qa_report.py
python -m pytest test_precision.py -v
python -m pytest tests/ -v
```

Note: some scraper commands depend on local environment variables, Playwright browsers, Excel outputs, local DB or network access.

## Last Known Validation

After creating the minimal Next.js app:

- `npm install` passed.
- `npm run typecheck` passed.
- `npm run lint` passed.
- First `npm run build` failed due BOM encoding in JSON files.
- BOM was fixed.
- `npm run build` passed.
- `npm test` passed as placeholder.
- `npm run validate` passed.

Security note: `npm install` reported 3 moderate vulnerabilities. No automatic `npm audit fix` was run because that may change dependency versions outside this task scope.

## Current CI

`.github/workflows/ci.yml` still reflects the older CI shape and should be updated in a later explicit task.

Known limitations:

- CI may still check old root frontend assumptions.
- CI may not yet run root `npm run validate`.
- Ruff currently does not fail CI because of `--exit-zero`.
- Full `scrapers/tests/` suite is not guaranteed in CI.

## Missing Sensors

Pending sensors to add:

- Format check.
- Real unit tests for `apps/web`.
- Event quality checks.
- Secret scanning.
- Manual mobile QA checklist execution.
- Broken link/image checks for event cards.
- Data contract validation between Event Intelligence and frontend.
- CI update for the workspace structure.

## Manual Mobile QA

Use `docs/checklists/manual-qa.md` once a V0 UI exists.

## Completion Rule

No task should be marked complete unless:

- Relevant commands were run, or
- The reason they could not run is documented, and
- The missing validation is listed as follow-up.
