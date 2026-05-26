# ADR-004: Auth And Personalization

## Status

Accepted for V0.

## Context

Personalization can improve discovery but introduces privacy, security and product complexity.

## Decision

V0 has no login, no persistent favorites and no behavioral personalization.

V1 may add registered users with explicit preferences.

V2 may add behavioral personalization only with consent, retention policy and deletion controls.

## Consequences

- No auth implementation in V0.
- No personal data storage in V0.
- No tracking-based recommendations in V0.
- Future personalization must be designed with privacy from the start.

## Open Questions

- Auth provider: TBD — requires user decision.
- Preference taxonomy: TBD — requires user decision.
- Retention duration: TBD — requires user decision.
