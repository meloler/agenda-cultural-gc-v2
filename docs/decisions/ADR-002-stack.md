# ADR-002: Stack

## Status

Proposed. TBD — requires user decision.

## Context

The current frontend is a vanilla JS SPA in the repository root. The rebuild should prepare a future app in `apps/web/`, but the stack has not been chosen.

## Decision

No final stack decision yet.

The repo will prepare for `apps/web/` as the future app location, while preserving the current frontend until a legacy move is approved.

## Options To Evaluate

- Vanilla/Vite.
- React/Vite.
- Next.js.
- Other lightweight mobile-first setup.

## Decision Criteria

- Mobile-first speed.
- Simple deployment.
- Easy testing.
- Low maintenance.
- Good developer/agent ergonomics.
- Works with Supabase or curated event exports.

## Consequences

- No UI scaffold should be built until stack is chosen.
- Harness docs can proceed without stack lock-in.
