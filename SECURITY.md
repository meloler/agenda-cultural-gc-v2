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
