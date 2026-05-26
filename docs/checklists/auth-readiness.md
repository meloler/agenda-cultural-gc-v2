# Auth Readiness Checklist

## Purpose

This checklist defines the conditions that must all be met before V1 auth (registered
users) is activated. Do not implement login until all items are checked.

## Architecture

- [ ] Auth provider is decided and documented in ADR-004.
- [ ] Supabase Auth (or chosen provider) is configured in a non-production environment.
- [ ] `SUPABASE_SERVICE_ROLE_KEY` is confirmed absent from all `apps/web` source files.
- [ ] Public anon key only is used in frontend.
- [ ] Server-side token exchange or edge function is designed for any privileged operation.

## Database Migrations

- [ ] V1 schema migrations are written and reviewed.
  - [ ] `user_profile` table.
  - [ ] `user_interest` table.
  - [ ] `saved_event` table.
  - [ ] `event_feedback` table.
  - [ ] `personalization_consent` table.
- [ ] Migrations are tested in a staging/branch environment before production.
- [ ] Rollback path for each migration is documented.

## Row Level Security

- [ ] RLS is enabled on all V1 user tables.
- [ ] `user_profile`: user reads/writes only their own row.
- [ ] `user_interest`: user reads/writes only their own rows.
- [ ] `saved_event`: user reads/writes only their own rows.
- [ ] `event_feedback`: user reads/writes only their own rows.
- [ ] `personalization_consent`: user reads/writes only their own row.
- [ ] Unauthenticated users cannot read any V1 table rows.
- [ ] Service role bypass is only used in trusted server/pipeline contexts.

## Auth Flow

- [ ] Sign up flow is implemented and tested.
- [ ] Sign in flow is implemented and tested.
- [ ] Sign out flow is implemented and tested.
- [ ] Password reset or magic link flow is implemented and tested.
- [ ] Session persistence behavior is documented.
- [ ] Token expiry and refresh behavior is documented.

## V0 Preservation

- [ ] Unauthenticated users can still browse the full V0 discovery experience.
- [ ] No V0 page requires login to render.
- [ ] Mock fallback still works for unauthenticated contexts.
- [ ] Registration is never forced for basic browsing.
