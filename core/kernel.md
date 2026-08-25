<!-- securable-kernel v1 · source of truth. Bindings are GENERATED from this file by scripts/build_bindings.py — edit here, then rebuild. Size budget enforced by the builder. -->
## Securable engineering (always apply)

1. **Parse, don't trust.** Input crossing a trust boundary (HTTP/RPC, queue, file, CLI, env, webhook, foreign DB rows) is parsed once at the boundary into a typed structure — only expected named fields, failing closed.
2. **Authority is server-side.** Identity, ownership, tenancy, role, and money/state come from authenticated server-side sources, never from client-supplied values or unverified claims.
3. **Never emit:** string-built SQL/shell/paths; JWT verification without pinned algorithm+audience+issuer; mass assignment from raw request bodies; bare catch-alls or silent failure; unbounded reads; external calls without timeouts; secrets in code/logs/errors; non-constant-time secret comparison.
4. **Observable security.** Security-relevant actions emit structured events (actor, action, target, outcome); failure paths log; errors shown to callers never leak internals.
5. **Securability Notes.** Close security-relevant work with 2–4 lines: boundaries handled, decisions a reviewer must see, anything unverified.

If `.securable/requirements.yaml` exists it is the authoritative security-requirements source: implement to its acceptance criteria and flip `status` planned→implemented only. Depth on demand via the securable skills: securability-engineering (generation) · securability-engineering-review (SSEM scoring) · prd-securability-enhancement (requirements) · fiasse-lookup (reference).
