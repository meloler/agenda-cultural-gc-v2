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

Status: this now runs real Vitest unit tests for `packages/event-intelligence`.
It also runs real Vitest unit tests for `apps/web` home collection presentation.

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

Current `apps/web` tests cover:

- Non-publishable mock events are excluded from the home.
- Mock data appears in at least five MVP collections.
- Events are sorted by descending Event Intelligence score inside each collection.
- Main intention chips are available.
- The mock data set is present and varied.
- Supabase rows map to the Event Intelligence model.
- Supabase rows without valid dates do not appear in collections.
- Missing public Supabase config produces controlled fallback.
- Real-like events are still ordered by Event Intelligence score.
- Frontend source does not reference the Supabase service role key.
- Event detail lookup returns publishable events and rejects non-publishable ones.
- Detail components render date, place and price.
- Safe external links reject unsafe schemes and set `target`/`rel` correctly.
- Home cards link to `/events/[id]`.
- Past events do not outrank upcoming events.
- Empty event lists and optional missing fields do not break collection generation.
- Production fallback messaging does not silently hide missing Supabase configuration.
- Local event quality report counts rejected and incomplete events.

### packages/event-intelligence

From `packages/event-intelligence/` or through npm workspace:

```bash
npm run typecheck
npm run lint
npm test
npm run validate
```

Vitest is used for FEAT-001 because the Event Intelligence layer is pure TypeScript, deterministic and benefits from fast unit tests without browser setup.

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

After implementing FEAT-001:

- `npm install` passed.
- `npm run typecheck` passed.
- `npm run build` passed.
- `npm run lint` passed.
- `npm test` passed with 14 real Event Intelligence tests.
- `npm run validate` passed.

After implementing FEAT-002:

- `npm run typecheck` passed.
- `npm run lint` passed with one non-blocking Next image warning for mock images.
- `npm test` passed with 19 real tests total.
- `npm run build` passed after removing BOM from package JSON files and configuring local package transpilation.
- `npm run validate` passed.

After implementing FEAT-003:

- `npm run typecheck` passed.
- `npm run lint` passed with one non-blocking Next image warning for mock images.
- `npm test` passed with 25 real tests total.
- `npm run build` passed.
- `npm run validate` passed.

After implementing FEAT-004:

- `npm run typecheck` passed.
- `npm run lint` passed with two non-blocking Next image warnings for mock/external images.
- `npm test` passed with 33 real tests total.
- `npm run build` passed.
- `npm run validate` passed.

After implementing FEAT-005:

- `npm run typecheck` passed.
- `npm run lint` passed with two non-blocking Next image warnings for mock/external images.
- `npm test` passed with 41 real tests total.
- `npm run build` passed.
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

## Required Sensors Before V1 Auth Implementation

These tests do not exist yet because auth is not implemented. They must all pass before
V1 login and personalization can be activated. Do not implement them prematurely.

### Auth Flow

- Sign up flow creates a valid authenticated session.
- Sign in flow returns a valid authenticated session.
- Sign out flow invalidates the session.
- Unauthenticated requests to V1 personal data endpoints are rejected.

### Row Level Security / Tenant Isolation

- User A cannot read user B's `user_profile` row.
- User A cannot read user B's `user_interest` rows.
- User A cannot read user B's `saved_event` rows.
- User A cannot read user B's `event_feedback` rows.
- User A cannot read user B's `personalization_consent` row.
- Service role bypass does not apply to frontend anon key requests.

### Personal Data Controls

- User can update their own `user_profile`.
- User can delete their own `user_profile` and all related V1 rows.
- User can export a list of their saved events.
- Deleting account removes all V1 personal data.

### Consent Gate

- `behavioral_personalization_enabled` defaults to `false` for new users.
- Behavioral signals are not collected without explicit V2 consent.
- `explicit_preferences_enabled` must be `true` before preferences are stored.

### V0 Preservation

- Unauthenticated users can still browse all V0 discovery collections.
- No V0 page returns a login redirect for anonymous requests.
- Mock fallback still works for unauthenticated contexts.

### Security

- `SUPABASE_SERVICE_ROLE_KEY` does not appear in any `apps/web` source file.
- Preference data does not appear in server logs or error responses.

## Manual Mobile QA

Use `docs/checklists/manual-qa.md` once a V0 UI exists.

## Completion Rule

No task should be marked complete unless:

- Relevant commands were run, or
- The reason they could not run is documented, and
- The missing validation is listed as follow-up.
