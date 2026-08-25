# The Securable Contract

Repo-resident, machine-readable securability requirements — the artifact that
makes this pack elevate *any* code-generation harness, not just the one it is
loaded into. A prompt influences one assistant for one session; a contract in
the repository binds every assistant, every session, and every human reviewer
that touches the code.

This is FIASSE v1.1 **S4.1 (Clear Expectations)** made durable, with the
lifecycle meeting the code at the merge (**S5.2**).

## The files

| File | Purpose | Schema |
|---|---|---|
| `.securable/requirements.yaml` | Per-feature security requirements with ASVS 5.0 references, testable acceptance criteria, and a lifecycle `status` | `schema/securable/requirements.schema.json` |
| `.securable/boundaries.yaml` | The system's trust-boundary map: entry points, data classes, and the server-side authority behind each boundary (S4.2, S4.3) | `schema/securable/boundaries.schema.json` |

Worked examples: [`examples/securable/`](../examples/securable/). Both files
live in the **consuming project**, not in this pack.

## The lifecycle

```
planned ──────────► implemented ──────────► verified
  PRD skill           generation             review skill /
  (or a human)        (any harness)          securability report / CI
```

- **`planned`** — written by `prd-securability-enhancement` (Step 7) or by hand.
  Every requirement carries at least one behaviorally testable acceptance
  criterion; an entry without one is a control citation, not a requirement
  (S6.1.1), and the validator's schema pressure exists to keep that distinction.
- **`implemented`** — flipped by whatever generates or edits the code, in any
  harness, when it believes the acceptance criteria are satisfied. The
  securability kernel and the generation skill both instruct this flip. An
  `implemented` claim is exactly that — a claim.
- **`verified`** — flipped only by something that *checked*: the review skill,
  the merge-time securability report, or a CI test. Requires `evidence`
  (file:line, test name, report reference). Generators never set `verified`;
  the validator rejects `verified` without evidence.

A refuted `implemented` claim is a review finding, not a silent downgrade.

## Validation

```bash
python3 scripts/validate_securable.py --dir .securable
```

Beyond shape, the validator enforces the rules a generic schema cannot:

- requirement ids belong to their feature (`F-03-R2` lives under `F-03`)
- a requirement whose `level` exceeds the baseline `asvs_level` must carry
  `escalation: true` — above-baseline items are explicit escalations, never
  silently smuggled into the baseline
- `verified` requires `evidence`
- feature `boundaries` must exist in `boundaries.yaml` when both files exist
- **every ASVS reference must resolve against the bundled ASVS 5.0 catalog**
  (`data/asvs/`) — down to the individual requirement id. Citing a requirement
  that does not exist is the failure mode that motivated this validator; in a
  consuming repo without the catalog, format is still enforced and existence
  checking degrades to a warning.

Tests: `python3 tests/securable-contract/test_validate.py` (the valid example
plus twelve invalid mutations, each asserted to fail for its specific reason).

## Why a contract and not a prompt

FIASSE's aim is security integrated into ordinary engineering without breaking
flow. The contract serves that in three ways a prompt cannot:

1. **Tool independence.** opencode today, Claude Code tomorrow, a human with an
   editor on Friday — the requirements don't care which.
2. **Reviewability.** Requirements changes show up in diffs and get reviewed
   like code. Security expectations stop living in chat scrollback.
3. **Traceability without theater.** `status` + `evidence` says exactly what
   is claimed versus checked — the same honesty discipline as the review
   skill's `Not assessed`.
