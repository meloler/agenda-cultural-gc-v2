# Risks

## Critical Risks

### R1 — Breaking The Existing Pipeline

`scrapers/` contains valuable scraping, enrichment, geolocation and export work. Rewriting it prematurely could destroy working knowledge.

Mitigation: preserve `scrapers/`, add tests and quality gates before changes.

### R2 — Product Drift Back To Chronological Agenda

The current frontend naturally encourages lists, filters and calendar views.

Mitigation: V0 must start from dynamic collections and user intent.

### R3 — No Data Contract

The frontend consumes event rows directly. That couples UI to database shape.

Mitigation: define a curated event contract and Event Intelligence layer.

### R4 — Weak Validation Sensors

Current frontend has no real lint/typecheck/tests. Current CI does not fully protect the repo.

Mitigation: add baseline format, lint, typecheck, unit tests, build and mobile smoke checks.

### R5 — Secrets Exposure

Supabase keys and service role keys can be misused if placed in frontend or docs.

Mitigation: use environment variables, never expose service role key to frontend, add secret scanning.

### R6 — Too Many New Sources Too Quickly

Adding many scrapers increases noise, duplicates and maintenance.

Mitigation: add sources in small measured batches.

### R7 — V1/V2 Privacy Debt

Preferences and behavior tracking create personal-data obligations.

Mitigation: V0 anonymous only. V1/V2 require consent, retention and deletion design.

## Open Risks

- Stack choice for `apps/web/`: TBD — requires user decision.
- Supabase schema changes needed for Event Intelligence: TBD — requires user decision.
- Final cheap-price threshold: TBD — requires user decision.
- Whether legacy frontend remains deployable during rebuild: TBD — requires user decision.

## R8 — npm audit moderate vulnerabilities

Status: open.

`npm audit --json` currently reports 3 moderate vulnerabilities:

- `postcss` `<8.5.10`: moderate XSS advisory `GHSA-qx2v-qp2m-jg93`, pulled transitively through `next`.
- `next`: moderate because it depends on the vulnerable `postcss` range reported by npm audit.
- `ws` `>=8.0.0 <8.20.1`: moderate uninitialized memory disclosure advisory `GHSA-58qx-3vcg-4xpx`, transitive dependency.

Impact assessment:

- Current `apps/web` is a placeholder and does not connect to production data or Supabase.
- `postcss`/`next` affect the web build/runtime dependency chain and should be reviewed before production deployment.
- `ws` appears transitive/development/runtime tooling related and should be reviewed with dependency updates.

Action recommended:

- Do not run `npm audit fix --force` blindly; npm suggests a major/incoherent downgrade path for `next` in this environment.
- Re-run audit after dependency updates or when Next/PostCSS patched versions are available.
- Treat this as a blocker before production deployment, not a blocker for local scaffold work.

## R9 — Real Data Quality Still Needs Manual Review

Status: open.

Automated checks now verify publishable-event rules, safe links, fallback behavior and core collection ordering. They do not prove that real Supabase rows are editorially good.

Known limitations:

- Legacy `evento.lugar` may mix venue, address and municipality.
- Image quality is not manually reviewed by tests.
- Official links are checked for safe URL scheme, not for live HTTP success.
- Browser-level mobile QA is documented but still manual.

Action recommended:

- Run `docs/checklists/manual-qa.md` on real data before production deployment.
- Run `docs/checklists/event-quality.md` on a representative Supabase export.
- Add automated link/image checks later under FEAT-005 follow-up or CI hardening.
