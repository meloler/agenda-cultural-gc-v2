# Security

## Secrets

- Do not commit real secrets, tokens, API keys or credentials.
- Do not document real secret values.
- `.env` files must stay local and untracked.
- `.env.example` may contain placeholder values only.

## Supabase

- Frontend may use only public anon key when appropriate.
- Never expose `SUPABASE_SERVICE_ROLE_KEY` in frontend code, static assets, logs or docs.
- Service role operations must run only in trusted server/local pipeline contexts.
- Use minimum necessary permissions.

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

## V1/V2 Personal Data

Registered users, preferences and behavioral personalization require:

- Explicit consent.
- Clear purpose.
- Retention policy.
- Deletion controls.
- Export/access controls where applicable.
- Ability to opt out.

No behavioral personalization in V0.

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
