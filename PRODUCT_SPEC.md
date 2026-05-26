# Product Spec

## One-Line Definition

Agenda Cultural GC is a mobile-first plan discovery guide for Gran Canaria, organized by dynamic intent-based collections instead of a chronological agenda.

## Product Goal

Help people decide what to do quickly, especially on mobile, using curated and explainable event collections.

## Target Experience

A user opens the app and sees collections like:

- Top planes de hoy.
- Este finde.
- Gratis o baratos.
- Con niños.
- Música en directo.
- Teatro y escena.
- Mercadillos y ferias.
- Joyas escondidas.

The user should not need to understand event sources, scraping, categories or database structure.

## MVP V0

### Included

- Anonymous mobile-first home.
- Intention cloud.
- Dynamic collections.
- Simple auditable ranking.
- Event card.
- Event detail page.
- Clear reason why an event appears in a collection.
- Mock-data support for early UI development.

### Home V0 Shape

The first home experience is a mobile-first discovery surface, not a calendar.

It contains:

- A simple header with the product name and a short discovery promise.
- A hero asking: "¿Qué plan te apetece?"
- An intention cloud with quick prompts such as Hoy, Este finde, Gratis, Con niños, Música and Teatro.
- Horizontal collection rails generated from Event Intelligence.
- Event cards focused on fast decisions: what, when, where, price, category and why it appears.

Current home data behavior:

- If public Supabase variables are configured, the home can load curated real events.
- If Supabase is not configured or fails, the home falls back safely to mock data.
- In both cases, events pass through Event Intelligence before appearing in collections.

### Event Detail V0 Shape

The event detail page is optimized for quick mobile decision-making.

It contains:

- A visual hero with image or fallback placeholder.
- Event title and primary category/tag.
- Date, time when available, place, address when available, price and source.
- 2-4 explainable recommendation reasons from Event Intelligence.
- A safe external CTA only when the official URL uses `http` or `https`.
- A clear back link to the home.

The page does not include login, favorites, personalization, tracking or interactive maps.

### Excluded

- Login.
- Persistent favorites.
- Behavioral personalization.
- Admin panel.
- Push notifications.
- Payments.

## Collection Definitions

### Top planes de hoy

Events happening today, ranked by freshness, quality and relevance.

### Este finde

Friday evening through Sunday. Exact cutoff TBD — requires user decision.

### Gratis o baratos

Free events or low-price events. Cheap threshold TBD — requires user decision.

### Con niños

Family-friendly events based on category, keywords, source metadata and venue context.

### Música en directo

Concerts, live music, jams and music events.

### Teatro y escena

Theater, dance, performance, comedy and stage events.

### Mercadillos y ferias

Markets, fairs, artisan, gastro and local product events.

### Joyas escondidas

Smaller or less obvious events with good quality signals and lower mainstream visibility. Exact ranking formula TBD — requires user decision.

## Ranking Principles

Ranking must be simple and explainable in V0.

Possible scoring inputs:

- Is the event soon?
- Is the date reliable?
- Is the place clear?
- Is there an image?
- Is there a useful description?
- Is there a price or clear free signal?
- Is it relevant for the current collection?
- Is the source trusted?

## Event Quality Principles

V0 should prefer fewer reliable plans over many doubtful rows.

An event must not appear publicly unless it has:

- A title.
- A valid date.
- A clear place signal.
- A category or useful tags.
- A source name or official/source URL.

Incomplete events may still appear with lower score if they are publicable. Examples:

- Missing image.
- Missing hour.
- Missing description.
- Missing price.
- Missing coordinates.

Past events should not be prioritized in public discovery collections.

## Success Criteria V0

- A user can understand what to do today or this weekend without opening filters.
- Event cards are decision-oriented, not database-oriented.
- Every collection can explain why an event is there.
- The app works well on mobile first.
- The pipeline remains intact.

## Roadmap V1 And V2

This section documents planned future phases. No V1 or V2 feature is implemented yet.

### V1 — Registered User With Explicit Preferences (future)

V1 adds optional user registration. Registration is never mandatory for basic browsing.
V0 discovery continues to work fully without an account.

V1 scope:

- Optional account creation via email or managed auth provider.
- Preference onboarding: preferred municipality/zone, cultural interests, budget range,
  plans with children yes/no.
- Save events for later.
- Like / not interested per event.
- Simple collection reordering or filtering based on explicit preferences.

V1 explicitly excludes:

- Implicit behavioral tracking (view time, scroll, click history).
- Opaque recommendation models.
- Automatic notifications without explicit consent.
- Direct purchase or payment flow.
- Comments or reviews.
- Data sale or sharing with third parties.

V1 must not be implemented until:

- `docs/checklists/auth-readiness.md` is complete.
- `docs/checklists/personalization-readiness.md` is complete.
- RLS, migrations, auth flow tests and privacy review are done.
- A dedicated feature (post-FEAT-006) is defined and approved.

### V2 — Behavioral Personalization With Consent (future, separate)

V2 is a distinct future phase after V1 is stable and validated.

V2 may include behavioral personalization only if:

- Explicit opt-in consent per signal type is in place.
- Data minimization is enforced.
- Retention and deletion are defined and enforced.
- Personalization is explainable in plain language to the user.
- User can disable behavioral personalization without losing their account.
- Privacy review is completed.

V2 explicitly excludes:

- Any behavioral tracking without explicit consent.
- Selling or sharing behavioral data.
- Black-box recommendation models without explainability.

See `docs/decisions/ADR-004-auth-personalization.md` for the full decision record and
`docs/plans/active/user-personalization-v1.md` for the conceptual data model.
