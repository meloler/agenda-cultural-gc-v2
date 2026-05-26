# Manual QA Checklist

Use this checklist before marking a mobile-facing feature ready for review.

## Setup

- [ ] Run `npm run validate` from the repository root.
- [ ] Run `npm run dev` and open the app locally.
- [ ] Set browser viewport to 375px wide.
- [ ] Confirm no real secrets are needed for the review.
- [ ] Confirm whether the app is using Supabase or mock fallback banner.

## Home At 375px

- [ ] Header text is readable: `Agenda Cultural GC` and the short promise.
- [ ] Hero is visible without horizontal page overflow.
- [ ] Hero communicates discovery, not a chronological agenda.
- [ ] Intention chips are visible and each chip is at least finger-tappable.
- [ ] Chips can scroll horizontally without breaking the page.
- [ ] At least one collection rail is visible.
- [ ] Rails scroll horizontally and do not create full-page horizontal overflow.
- [ ] Event cards show title, date, place, price/category and a reason.
- [ ] Long event titles do not hide date, place or price.
- [ ] Empty home state is understandable if there are no publicable events.

## Event Detail At 375px

- [ ] Open an event card from the home.
- [ ] Detail page shows image or fallback placeholder.
- [ ] Title is readable and not visually crushed.
- [ ] Date and time are visible when present.
- [ ] Place and address/location are visible when present.
- [ ] Price or `Gratis`/unknown handling is visible.
- [ ] Source is visible.
- [ ] Recommendation reasons are readable and explain why the event appears.
- [ ] CTA is large, clear and tappable when a safe official URL exists.
- [ ] No CTA is shown when official URL is missing or unsafe.
- [ ] Back link returns to the home.

## States

- [ ] Loading state says recommendations are being prepared.
- [ ] Error state explains that doubtful data is not shown.
- [ ] Not-found detail state is clear and offers return home.
- [ ] Non-publicable detail state is clear and does not present the event as valid.
- [ ] Mock fallback state is visible when Supabase public config is absent.
- [ ] In production-like review, missing Supabase config is not silent.

## Accessibility Basics

- [ ] Images have meaningful alt text or accessible placeholder text.
- [ ] Buttons and links have readable text.
- [ ] Keyboard focus is visible on chips, cards, CTA and back links.
- [ ] The page has a sensible heading order.
- [ ] Meaning is not communicated by color only.

## External Links

- [ ] Safe official links open in a new tab.
- [ ] Safe official links use `noopener noreferrer`.
- [ ] Unsafe links such as `javascript:`, `data:` and `vbscript:` are not clickable.

## Notes

Record any failed item with:

- URL or screen.
- Viewport width.
- Event ID if relevant.
- What was expected.
- What happened.
