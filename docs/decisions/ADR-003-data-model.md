# ADR-003: Data Model

## Status

Proposed.

## Context

The current pipeline produces event records consumed by the frontend. The rebuild needs a stable event contract for dynamic collections.

## Decision

Introduce a curated event concept for frontend consumption and an Event Intelligence layer to derive publishability, scoring, collection membership and explanations.

## Minimum V0 Event Fields

- `id`
- `title`
- `description`
- `date`
- `time`
- `venue`
- `municipality`
- `image_url`
- `source_url`
- `price`
- `category`
- `quality_signals`
- `collections`
- `score`
- `reason`

Exact schema names are TBD — requires user decision.

## Event Intelligence Responsibilities

- Validate event publishability.
- Calculate simple scoring.
- Assign collections.
- Explain ranking.

## Consequences

- The new frontend should not depend directly on raw scraper internals.
- Supabase schema changes, if needed, require explicit review.
