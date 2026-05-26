# Plan: User Personalization V1 (Conceptual)

## Status

Conceptual — not yet started. Documented in FEAT-006 for future planning.

## Objective

Prepare the architecture, data model, privacy rules and readiness conditions for an
optional registered-user layer on top of the V0 anonymous experience.

This document does not authorize implementation. Implementation requires a new dedicated
feature (post-FEAT-006) with its own acceptance criteria and readiness conditions.

## Product Context

Agenda Cultural GC V0 is fully anonymous. The product must continue to work excellently
without an account. Registration is always optional, never a gate to basic discovery.

## V1 Scope

V1 adds optional user registration with explicit preferences only.

**Included in V1:**

- Optional account creation (email or managed provider via Supabase Auth).
- Preference onboarding on first registration:
  - Preferred municipality or zone in Gran Canaria.
  - Cultural interests (music, theater, family, markets, gastro, etc.).
  - Budget preference (free only, low budget, any).
  - Plans with children (yes / no / sometimes).
- Save events for later.
- Like / not interested per event.
- Simple collection reordering or filtering based on explicit preferences.

**Excluded from V1:**

- Behavioral tracking (view time, scroll depth, click history).
- Implicit signals from browsing.
- Opaque recommendation models.
- Automatic push notifications without explicit per-channel consent.
- Direct ticket purchase or payment flow.
- Comments, reviews or social features.
- Admin panel.
- Multi-account or organization features.

## V2 Scope (Future, Separate Feature)

V2 is a distinct future phase. It may include behavioral personalization only if:

- Per-signal explicit consent is in place.
- Data minimization is enforced.
- Retention and deletion controls are implemented.
- Personalization is explainable to the user.
- Privacy review is completed.
- User can opt out without losing their account.

## Conceptual Data Model

These entities define the future data contract. No migrations exist yet.
All entities are marked as conceptual and pending RLS design before implementation.

### user_profile

Stores user preferences collected explicitly during onboarding.

| Field | Type | Notes |
|-------|------|-------|
| user_id | uuid | FK to Supabase Auth user |
| display_name | text (optional) | User-chosen display name |
| preferred_municipality | text (optional) | e.g. Las Palmas, Telde, Agüimes |
| budget_preference | text (optional) | free \| low \| any |
| has_children_plan_interest | boolean (optional) | Wants family-friendly plans |
| created_at | timestamptz | Auto |
| updated_at | timestamptz | Auto |

RLS: user can read and write only their own row.

### user_interest

Stores explicit cultural interest tags collected during onboarding or preference editing.

| Field | Type | Notes |
|-------|------|-------|
| user_id | uuid | FK to Supabase Auth user |
| tag | text | e.g. música, teatro, familia, mercadillos |
| weight | integer | 1–5, explicit importance |
| source | text | explicit \| inferred (V2 only) |
| created_at | timestamptz | Auto |

RLS: user can read and write only their own rows.

Note: `source = 'inferred'` is reserved for V2 with explicit consent. V1 only uses
`source = 'explicit'`.

### saved_event

Stores events the user has saved for later.

| Field | Type | Notes |
|-------|------|-------|
| user_id | uuid | FK to Supabase Auth user |
| event_id | text | References `evento.id` from curated data |
| created_at | timestamptz | Auto |

RLS: user can read and write only their own rows. No cross-user access.

### event_feedback

Stores per-event like / not interested signals.

| Field | Type | Notes |
|-------|------|-------|
| user_id | uuid | FK to Supabase Auth user |
| event_id | text | References `evento.id` from curated data |
| feedback | text | like \| dislike \| not_interested |
| created_at | timestamptz | Auto |

RLS: user can read and write only their own rows. Feedback is private per user.

Note: `dislike` is reserved for V2. V1 uses only `like` and `not_interested`.

### personalization_consent

Tracks what the user has consented to and the version of the consent.

| Field | Type | Notes |
|-------|------|-------|
| user_id | uuid | FK to Supabase Auth user |
| explicit_preferences_enabled | boolean | User agreed to store explicit preferences |
| behavioral_personalization_enabled | boolean | V2 only — false until V2 is active |
| analytics_enabled | boolean | Optional analytics consent |
| consent_version | text | e.g. v1.0 |
| updated_at | timestamptz | Auto |

RLS: user can read and write only their own row.
`behavioral_personalization_enabled` must default to `false` and require V2 activation.

## Implementation Conditions

Do not start V1 implementation until:

- `docs/checklists/auth-readiness.md` is fully checked.
- `docs/checklists/personalization-readiness.md` is fully checked.
- `docs/checklists/privacy.md` V1 section is fully checked.
- RLS is designed and tested for all V1 entities.
- Auth flow tests are written.
- Tenant isolation tests are written.
- A privacy review is completed.
- A dedicated feature (FEAT-007 or equivalent) is defined and approved.

## Boundaries

- `scrapers/` must not be changed for V1.
- `legacy/frontend-static/` must not be changed.
- `vercel.json` must not be changed unless there is an explicit deployment task.
- V0 must continue to work anonymously even after V1 is activated.
- `SUPABASE_SERVICE_ROLE_KEY` must never appear in `apps/web` source.
