# Privacy Checklist

## V0 — Anonymous Discovery (current)

- [ ] No login.
- [ ] No persistent favorites.
- [ ] No behavioral personalization.
- [ ] No personal data storage.
- [ ] No service role key in frontend.
- [ ] No tracking of clicked URLs or user sessions.
- [ ] External links use `rel="noopener noreferrer"` and do not embed tracking parameters.
- [ ] Logs contain no personal identifiers.

## V1 — Registered User With Explicit Preferences (future)

Must satisfy all V0 items above, plus:

- [ ] Explicit consent is obtained before any preference is stored.
- [ ] Consent version is stored and auditable.
- [ ] Preferences collected are limited to the V1 scope:
  - Municipality/zone preference.
  - Cultural interest tags.
  - Budget preference.
  - Plans with children yes/no.
  - Saved events.
  - Like / not interested per event.
- [ ] No implicit behavioral signals are collected in V1.
- [ ] User can view all stored preferences at any time.
- [ ] User can edit all preferences at any time.
- [ ] User can delete their account and all associated data.
- [ ] Data retention period is defined, documented and enforced.
- [ ] Export/access path is documented.
- [ ] RLS is enabled on all V1 personal data tables.
- [ ] Preference data does not appear in operational logs or error traces.
- [ ] Registration is optional — V0 experience works without account.
- [ ] Service role key is absent from frontend source code.

## V2 — Behavioral Personalization With Consent (future, separate feature)

Must satisfy all V0 and V1 items above, plus:

- [ ] Behavioral tracking has explicit per-signal opt-in consent.
- [ ] `personalization_consent.behavioral_personalization_enabled` is `true` only after
  explicit opt-in.
- [ ] User can opt out of behavioral personalization without losing their account.
- [ ] User can delete all behavioral history independently of their account.
- [ ] Behavioral signals are minimized: only what is demonstrably used in ranking.
- [ ] Personalization behavior is explained to the user in plain language.
- [ ] No opaque recommendation models without explainability.
- [ ] No sale or sharing of behavioral data with third parties.
- [ ] No automatic push notifications without explicit per-channel consent.
- [ ] Logs do not contain behavioral payload or sensitive preference data.
- [ ] Privacy review is completed before V2 activation.
- [ ] Retention and deletion are enforced for all V2 signals.

## General Rules (All Phases)

- No real secrets, tokens or keys in code, docs or logs.
- No `SUPABASE_SERVICE_ROLE_KEY` in frontend.
- External event links: `http:` and `https:` only, no tracking schemes.
- Operational logs: source name, counts, status, errors — no personal payloads.
