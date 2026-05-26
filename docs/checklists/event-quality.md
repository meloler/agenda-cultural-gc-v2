# Event Quality Checklist

Use this checklist for mock data, Supabase rows and future curated exports before they reach the V0 discovery UI.

## Publishable Minimum

An event can appear publicly only if:

- [ ] It has a non-empty title.
- [ ] It has a valid `starts_at` / `fecha_iso` date.
- [ ] It has at least one clear location signal: venue, address or municipality/place.
- [ ] It has category or useful tags.
- [ ] It has source name or official/source URL.
- [ ] It is not a past event for public discovery collections.

## Allowed But Lower Quality

These do not block publishing, but should lower confidence or score:

- [ ] Missing hour.
- [ ] Missing image.
- [ ] Missing description.
- [ ] Missing price and no free signal.
- [ ] Missing coordinates.
- [ ] Generic place that cannot distinguish venue/address/municipality.

## Reject Or Manual Review

Reject or manually review if:

- [ ] Date is invalid, parser artifact or placeholder.
- [ ] Title is generic, empty or clearly malformed.
- [ ] Source URL is broken or unsafe.
- [ ] Event appears duplicated and this record has lower quality.
- [ ] Event is outside Gran Canaria.
- [ ] Event is an old/past event unless an archive context exists.
- [ ] Price/date/location conflicts with the official source.

## Supabase Contract Review

For legacy `evento` rows:

- [ ] `nombre` maps to title.
- [ ] `fecha_iso` plus optional `hora` maps to start date/time.
- [ ] `lugar` currently maps to venue and address; municipality remains approximate/TBD.
- [ ] `estilo` maps to category.
- [ ] `precio_num` maps to price; `0` means free.
- [ ] `imagen_url` maps to event image if safe and useful.
- [ ] `source_id` maps to source name.
- [ ] `url_venta` maps to official/source URL when safe.
- [ ] `latitud` and `longitud` map to coordinates when available.

## Collection And Ranking QA

- [ ] Event appears in a collection for a reason visible to a user.
- [ ] Score is explainable through Event Intelligence reasons.
- [ ] Incomplete publicable events rank below richer equivalent events.
- [ ] Past events do not outrank upcoming events.
- [ ] Hidden gem logic does not bury obviously useful mainstream plans.

## Local QA Report

Use the app-level quality report utility when changing event contracts:

- `apps/web/lib/events/quality-report.ts`

It counts:

- total events;
- publicable events;
- rejected events;
- past events;
- incomplete-but-publicable events;
- missing official URLs;
- quality issue frequencies.
