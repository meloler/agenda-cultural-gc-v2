# Security

## Secrets

- Do not commit real secrets, tokens, API keys or credentials.
- Do not document real secret values.
- `.env` files must stay local and untracked.
- `.env.example` may contain placeholder values only.

## Supabase

- Frontend may use only public keys through `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
- Never expose `SUPABASE_SERVICE_ROLE_KEY` in frontend code, static assets, logs or docs.
- Service role operations must run only in trusted server/local pipeline contexts.
- Use minimum necessary permissions.
- If public Supabase variables are missing, the frontend must fall back to mock data or a controlled empty/error state.
- Do not print Supabase keys or environment values in logs.
- In production-like contexts, missing Supabase configuration must be visible as a controlled warning, not hidden silently.

## Event Data

V0 deals with public event information:

- Event title.
- Date/time.
- Venue/place.
- Public URL.
- Public image.
- Public description.
- Public price or ticket info.

Avoid storing private user data in V0.

## External Event Links

- Render official event links only after URL validation.
- Allow only `http:` and `https:` schemes.
- Reject unsafe schemes such as `javascript:` and `data:`.
- External links must use `target="_blank"` with `rel="noopener noreferrer"`.
- Do not log clicked URLs or introduce tracking in V0.

## V1/V2 Personal Data

Registered users, preferences and behavioral personalization require:

- Explicit consent before any personal data is stored.
- Clear purpose communicated to the user.
- Retention policy defined and enforced.
- Deletion controls: user can delete all personal data and their account.
- Export/access: user can request a copy of their data.
- Ability to opt out of personalization without losing the account.
- No sale or sharing of personal data with third parties.
- No automatic notifications without explicit per-channel consent.

No behavioral personalization in V0.

### V1 Specific Rules

- Preferences are explicit only: municipality, interests, budget, has_children.
- No implicit signals (view time, scroll, click history) in V1.
- `SUPABASE_SERVICE_ROLE_KEY` must not appear in frontend code in V1 any more than in V0.
- RLS must be enabled and tested on all V1 personal data tables before activation.
- Preference data must not appear in operational logs or error traces.
- Consent version must be stored and auditable.

### V2 Specific Rules

- Behavioral personalization requires explicit opt-in per signal type.
- `personalization_consent.behavioral_personalization_enabled` must default to `false`.
- Behavioral signals are minimized to only what is demonstrably used.
- Personalization logic must be explainable to the user.
- Logs must never contain behavioral payload or sensitive preference data.
- Privacy review must be completed before V2 activation.
- User can delete all behavioral history independently of their account.

### Activation Gate

Do not activate V1 or V2 until:

- `docs/checklists/auth-readiness.md` is complete.
- `docs/checklists/personalization-readiness.md` is complete.
- `docs/checklists/privacy.md` relevant phase is complete.
- Required sensors in `TESTING.md` pass.

## Logging

- Do not log secrets.
- Do not log service role keys.
- Do not log personal data.
- Keep logs operational: source name, counts, status, errors without sensitive payloads.

## Dependency And Supply Chain

Minimum future sensors:

- Dependency audit.
- Secret scanning.
- CI checks for accidental committed artifacts.
- Review before adding new scraping dependencies.

## Production Safety

- No production deploys without explicit approval.
- No destructive migrations without explicit approval.
- No direct production data changes unless task explicitly requires it and the operation is documented.
