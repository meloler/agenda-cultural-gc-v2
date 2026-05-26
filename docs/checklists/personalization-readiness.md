# Personalization Readiness Checklist

## Purpose

This checklist defines the conditions that must all be met before V1 personalization
(explicit preferences, saved events, feedback) is activated.

Do not implement personalization features until all items are checked.
See also `docs/checklists/auth-readiness.md` — auth must be ready first.

## Privacy And Consent

- [ ] Consent flow is designed: user explicitly agrees before any preference is stored.
- [ ] Consent version is stored in `personalization_consent`.
- [ ] User can view what preferences are stored.
- [ ] User can edit all preferences at any time.
- [ ] User can delete all preferences and their account.
- [ ] Data retention period is defined and documented.
- [ ] Deletion deletes all V1 personal data (profile, interests, saved events, feedback).
- [ ] Export/access path is documented (user can request their data).

## V1 Preference Scope

- [ ] Preferences are explicit only: municipality, interests, budget, has_children.
- [ ] No implicit/behavioral signals are collected in V1.
- [ ] `user_interest.source` is always `explicit` in V1 (never `inferred`).
- [ ] `event_feedback.feedback` is limited to `like` and `not_interested` in V1.
- [ ] `personalization_consent.behavioral_personalization_enabled` defaults to `false`.

## Recommendation Logic

- [ ] Recommendation logic based on explicit preferences is documented.
- [ ] Recommendations are explainable: user can see why an event is shown first.
- [ ] No black-box model is used in V1.
- [ ] Recommendations degrade gracefully when preferences are sparse or absent.

## Security

- [ ] RLS is confirmed working (see auth-readiness.md).
- [ ] No preference data is logged in operational logs.
- [ ] No preference payload appears in error traces.
- [ ] Service role key is absent from frontend code.

## Testing

All tests listed under "Required Sensors Before V1 Auth Implementation" in `TESTING.md`
must pass before activating V1 personalization.

## V2 Gate

- [ ] `behavioral_personalization_enabled` is `false` for all V1 users.
- [ ] V2 behavioral features are blocked behind a separate consent and feature flag.
- [ ] No view-time, scroll or click signals are collected without V2 consent.
