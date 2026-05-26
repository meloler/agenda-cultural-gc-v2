# Playbook: Run Validation

Use `TESTING.md` as the source of truth.

Minimum documentation validation:

```bash
git status --short
git diff --stat
```

Current useful scraper validations:

```bash
cd scrapers
python -m pytest test_precision.py -v
python -m pytest tests/ -v
```

Current frontend build:

```bash
npm run build
```

Known gap: frontend lint/typecheck/unit tests are pending.

After validation, update `progress.md` with what ran and what could not run.
