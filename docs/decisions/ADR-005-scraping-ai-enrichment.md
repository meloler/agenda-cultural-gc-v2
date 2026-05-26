# ADR-005: Scraping And AI Enrichment

## Status

Accepted.

## Context

The repository already contains a substantial scraping pipeline with enrichment, classification, venue auditing, geolocation, sanitization, export and upload.

## Decision

Preserve `scrapers/` and the existing IA enrichment pipeline.

Do not rewrite `scrapers/` during the product harness phase.

Changes to scrapers require:

- Clear reason.
- Small scope.
- Validation plan.
- No destructive migrations.
- No secret exposure.

## Consequences

- Product rebuild focuses first on harness, Event Intelligence and new frontend architecture.
- Scraper improvements should be separate commits.
- Event quality metrics should be added before expanding sources aggressively.
