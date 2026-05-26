# Testing And Validation

This file documents real commands that exist now and sensors that still need to be added.

## Current Real Commands

### Frontend / Root

Install dependencies:

```bash
npm install
```

Build currently defined in `package.json`:

```bash
npm run build
```

This runs:

```bash
node scripts/inject_env.mjs
node scripts/generate_feeds.mjs
```

Current test command:

```bash
npm test
```

Status: not useful yet. It currently exits with `Error: no test specified`.

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

Note: some commands depend on local environment variables, Playwright browsers, Excel outputs, local DB or network access.

## Current CI

`.github/workflows/ci.yml` currently:

- Installs Python dependencies.
- Installs Playwright Chromium.
- Runs `ruff check . --exit-zero` in `scrapers/`.
- Runs `python -m pytest test_precision.py -v`.
- Runs a small model import smoke test.
- Checks that `index.html`, `app.js` and `style.css` exist.

Limitations:

- Ruff does not fail the CI because of `--exit-zero`.
- Full `scrapers/tests/` suite is not guaranteed in CI.
- No real frontend test exists.
- No frontend lint exists.
- No typecheck exists.
- No real build verification gate exists in CI.

## Missing Sensors

Pending sensors to add:

- Format check.
- Frontend lint.
- Frontend typecheck.
- Unit tests.
- Real build check.
- Event quality checks.
- Secret scanning.
- Manual mobile QA checklist.
- Broken link/image checks for event cards.
- Data contract validation between Event Intelligence and frontend.

## Manual Mobile QA

Use `docs/checklists/manual-qa.md` once a V0 UI exists.

## Completion Rule

No task should be marked complete unless:

- Relevant commands were run, or
- The reason they could not run is documented, and
- The missing validation is listed as follow-up.
