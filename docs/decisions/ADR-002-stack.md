# ADR-002: Stack

## Status

Accepted as provisional for rebuild V0. Assumption — to be validated.

## Context

The current frontend has been moved to `legacy/frontend-static/`. The rebuild needs a minimal, testable web app location that does not interfere with `scrapers/`.

## Decision

Use `apps/web` with Next.js + TypeScript for the new mobile-first web app.

Use npm workspaces from the repository root:

- Root: coordination scripts.
- `apps/web`: new Next.js app.
- `packages/event-intelligence`: future Event Intelligence package placeholder.

## Current Scope

This decision only establishes a minimal compilable shell.

It does not implement:

- FEAT-001 Event Intelligence.
- Product home collections.
- Supabase connection.
- Login.
- Personalization.

## Consequences

- Root `npm run build` now builds `apps/web`.
- Root `npm run validate` runs typecheck, lint, build and the current test placeholder.
- `vercel.json` still needs a separate deployment/config decision.
- Legacy env/feed scripts remain in `scripts/` for now and are not part of the new app path.

## Open Questions

- Whether final hosting uses Vercel project root `apps/web` or root workspace build settings: TBD — requires user decision.
- Whether Event Intelligence runs in Python, TypeScript or both: TBD — requires user decision.
