# Event Intelligence

Pure TypeScript rules for deciding whether an event can be published, scoring its usefulness, assigning MVP discovery collections and explaining ranking signals.

This package is deterministic and does not connect to Supabase, production services, secrets or AI providers.

## Current V0 Assumptions

- Cheap event threshold: `10` euros. TBD — requires user decision.
- Weekend collection: Saturday/Sunday upcoming from `context.now`. Friday evening cutoff remains TBD — requires user decision.
- Hidden gem rule: publishable event with decent score, but without strong mainstream/source signals. TBD — requires user decision.
- Duplicate signal: inferred only from tags such as `duplicate`, `duplicado` or `posible duplicado` until a real dedupe field exists. TBD — requires user decision.
