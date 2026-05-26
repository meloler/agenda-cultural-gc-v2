# Roadmap

## Phase 0 — Harness And Safety

Goal: prepare the repo for controlled agentic development.

- Create product harness docs.
- Capture architecture and product decisions.
- Define validation expectations.
- Keep `scrapers/` untouched.
- Keep frontend in place until legacy move is approved.

## Phase 1 — Legacy Quarantine

Goal: preserve the current frontend without letting it shape the rebuild.

- Map current frontend files.
- Move current frontend to `legacy/frontend-v5/` only after approval.
- Keep current deployment safe.
- Add minimum build/test sensors.

## Phase 2 — Event Intelligence V0

Goal: create the event decision layer.

- Define publishable event rules.
- Define scoring formula.
- Define collection assignment rules.
- Add explanations for ranking/collection membership.
- Validate against sample data.

## Phase 3 — Mobile Discovery App V0

Goal: build anonymous mobile-first discovery experience.

- Create `apps/web/` shell.
- Build home with dynamic collections using mock data.
- Build event detail page.
- Add mobile QA checklist.
- Connect to curated source only after mock UX is stable.

## Phase 4 — Data Connection

Goal: connect V0 UI to curated event data.

- Use Supabase or curated export as source. TBD — requires user decision.
- Add data adapter.
- Validate event quality and broken links.
- Keep service role key out of frontend.

## Phase 5 — V1 Preferences

Goal: add registered user with explicit preferences.

- Authentication. TBD — requires user decision.
- Explicit preference selection.
- Privacy/security review.

## Phase 6 — V2 Personalization

Goal: behavioral personalization only with consent.

- Consent model.
- Retention policy.
- Deletion/export controls.
- Explainable personalization.
