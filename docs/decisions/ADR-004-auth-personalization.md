# ADR-004: Auth And Personalization

## Status

Proposed — not yet implemented. Reviewed for V1/V2 planning in FEAT-006.

## Context

Agenda Cultural GC is a mobile-first event discovery guide for Gran Canaria.

V0 is fully anonymous: no login, no personal data, no tracking. The product must work
excellently without any account. Discovery is organized by dynamic collections and
intent signals — not by user history.

Personalization can improve discovery quality but introduces legal obligations (GDPR,
privacy-by-design), technical complexity (auth, RLS, migrations, consent flows), and
product risk (forcing login reduces reach).

This ADR documents the planned path from V0 → V1 → V2 and the conditions that must
be met before each phase is activated.

## Decision

### V0 — Anonymous Discovery (current)

- No login.
- No user accounts.
- No persistent favorites or saved events.
- No behavioral tracking.
- No personal data storage.
- No service role key in frontend.
- The product must work fully and well for an anonymous visitor.

### V1 — Registered User With Explicit Preferences (future, not yet started)

V1 may add optional user registration. Registration is never mandatory for basic browsing.

V1 scope — explicit preferences only:

- Email or managed auth provider.
- Preference onboarding: municipality/zone, cultural interests, budget range, plans with
  children yes/no.
- Save events for later.
- Like / not interested feedback per event.
- Simple recommendations based on explicit preferences only.

V1 explicitly excludes:

- Implicit behavioral tracking.
- View time or scroll signals.
- Opaque recommendation models.
- Black-box personalization.
- Data sale or sharing with third parties.
- Automatic notifications without explicit consent.
- Direct purchase flow.
- Comments or reviews.

**V1 must not be implemented until all conditions in `docs/checklists/auth-readiness.md`
and `docs/checklists/personalization-readiness.md` are satisfied.**

### V2 — Behavioral Personalization With Consent (future, not yet planned)

V2 may add optional behavioral personalization only if:

- Explicit user consent is obtained per signal type.
- Data minimization is enforced (collect only what is used).
- Retention period is defined and enforced.
- User can delete all behavioral history.
- User can export their data.
- Personalization behavior is explained to the user in plain language.
- User can disable personalization without losing the account.
- Logs do not contain sensitive preference payloads.
- Privacy review is completed before activation.

V2 is a separate future feature. It must not bleed into V1 scope.

## Auth Provider Decision

Recommended: **Supabase Auth**, if the project remains on Supabase.

Rationale:
- Consistent with the existing data layer.
- Row Level Security integrates directly.
- Avoids a second vendor.
- Managed auth with email, magic link or OAuth providers.

Alternatives considered:

| Option | Assessment |
|--------|-----------|
| No login permanently | Valid. V0 discovery is a complete product. Revisit only when preference personalization has clear user demand. |
| Supabase Auth | Recommended if Supabase stack is maintained. |
| Clerk / Auth0 | Valid if more advanced auth UX is needed (SSO, enterprise, fine-grained session control). Higher cost and second vendor dependency. |
| Custom auth | Rejected unless there is a strong specific need. Custom session/token management introduces security debt. |

## Consequences

- No auth implementation in V0.
- No personal data storage in V0.
- No tracking-based recommendations in V0.
- V1 implementation requires migrations, RLS, privacy review and dedicated feature work.
- Row Level Security must be configured and tested before any real user data is stored.
- `SUPABASE_SERVICE_ROLE_KEY` must never appear in frontend code even in V1.
- V1 should not activate until RLS, auth flow tests, tenant isolation tests, consent flow
  and privacy checklist are all complete.

## Risks

- R-AUTH-1: RLS misconfiguration can expose one user's data to another.
- R-AUTH-2: Forcing login in V0/V1 reduces reach and trust.
- R-AUTH-3: Behavioral personalization before consent creates GDPR obligations.
- R-AUTH-4: Opaque recommendations reduce explainability and user trust.
- R-AUTH-5: Personalizing too early introduces product complexity before validating demand.

See also `RISKS.md` for project-level risk register entries.

## Signals To Revisit

This ADR should be revisited when:

- User research shows a clear demand for saved events or personalized collections.
- The product is deployed and has active users.
- The team has capacity to implement auth, migrations, RLS and privacy design properly.
- A privacy review is available.

## Related Documents

- `SECURITY.md` — secret handling and personal data rules.
- `docs/checklists/privacy.md` — V0/V1/V2 privacy checklist.
- `docs/checklists/auth-readiness.md` — conditions required before activating V1 auth.
- `docs/checklists/personalization-readiness.md` — conditions required before activating
  V1 personalization features.
- `docs/plans/active/user-personalization-v1.md` — conceptual V1/V2 plan and data model.
- `ARCHITECTURE.md` section: Future Auth And Personalization Architecture.
- `PRODUCT_SPEC.md` section: Roadmap V1 And V2.
- `RISKS.md` entries: R-AUTH-1 through R-AUTH-6.
- `TESTING.md` section: Required Sensors Before V1 Auth Implementation.
