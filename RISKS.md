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
