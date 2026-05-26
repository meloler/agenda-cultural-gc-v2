# Playbook: Review PR

Review in this order:

1. Product fit: does it support mobile-first discovery?
2. Safety: no secrets, no production/deploy surprises.
3. Scope: no unrelated rewrites.
4. Scrapers: preserved unless explicitly scoped.
5. Data contract: clear input/output shape.
6. Validation: tests/build/checks documented.
7. UX: mobile-first and decision-oriented.
8. Documentation: `progress.md` and relevant docs updated.

Block if service role keys appear in frontend or docs.
