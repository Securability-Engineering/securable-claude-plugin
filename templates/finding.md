# SSEM Finding Template

Use this structure for individual findings produced by the `securability-engineering-review` skill. Findings describe **engineering-attribute deficits**, not exploits. FIASSE v1.1 does not borrow CVSS, CWE, or CVE: those belong to assurance tools, not the SSEM rubric.

````markdown
### [SEVERITY] Title: [SSEM Attribute] Deficit

- **SSEM Pillar**: Maintainability | Trustworthiness | Reliability
- **SSEM Attribute**: Analyzability | Modifiability | Testability | Observability | Confidentiality | Accountability | Authenticity | Availability | Integrity | Resilience
- **FIASSE Reference**: FIASSE v1.1 S{section} (e.g., FIASSE v1.1 S4.4.1.2 for Isolated Integrity)
- **Pattern Tag**: From the Pattern Tag Reference in the review skill (e.g., "Isolated Integrity violation", "Canonical parsing gap", "Trust boundary input handling", "Silent failure")
- **Scope**: Systemic | Local — is this the codebase's default pattern, or a deviation from an otherwise sound practice?
- **Location**: `file_path:line_number` or component / module name. For a systemic finding, cite 2-3 representative sites and state how many exist.
- **Current State**: What the code does today (1-2 sentences)
- **Evidence**: Code snippet, configuration excerpt, or trace observation that demonstrates the deficit
- **Impact**: Effect on the named attribute and on the system's ability to remain securable. State which attribute this pulls down and by roughly how much.
- **Remediation**: Specific engineering improvement with a concrete code shape (the reader should be able to open a PR from this text). For a systemic finding, remediation is the convention, helper, or boundary — not a list of individual edits.
- **Expected Improvement**: +[X.X] on [Attribute] (list each attribute the fix lifts, e.g., "+5.0 on Integrity, +3.0 on Accountability")
- **Verification**: How to confirm the improvement landed: a test, a log line, a metric, or a re-review checkpoint
- **Confidence**: HIGH | MEDIUM | LOW (how certain is this finding)
````

## Severity Definitions

Severity reflects engineering impact on SSEM attribute scores and on the system's ability to remain securable. All thresholds are in **attribute points** — never pillar points, since a pillar mean moves by different amounts depending on whether it holds three or four attributes. Defined in [skills/securability-engineering-review/SKILL.md](../skills/securability-engineering-review/SKILL.md#severity-classification-for-individual-findings).

- **CRITICAL**: Drives a single attribute to ≤2 through systemic absence (no input parsing anywhere, no audit trail, ambient client-trust); or this finding owns the weakest attribute and the floor is binding on the overall score. Remediation requires architectural change.
- **HIGH**: Drives a single attribute to ≤4; or reduces one attribute by ≥3.0 points. Localized but pervasive.
- **MEDIUM**: Reduces one attribute by 1.0–2.9 points. Remediation contained to one module.
- **LOW**: Reduces one attribute by ≤0.9 points. Localized engineering improvement.
- **INFO**: Best-practice observation; no measurable attribute impact.

## Confidence Levels

- **HIGH**: Confirmed via direct code inspection of the cited `file:line`, with full context understood.
- **MEDIUM**: Strong indicators from code inspection, but some context unverified (e.g., upstream caller, runtime configuration): flag for manual verification.
- **LOW**: Heuristic match; pattern recognized but full context not inspected. May be false positive.

## Authoring Guidance

- **Anchor every finding in code**: a finding without a `file_path:line_number` (or named component) is a recommendation, not a finding.
- **Name the principle**: use a tag from the Pattern Tag Reference. "The auth is sketchy" is not a finding; "Isolated Integrity violation (FIASSE v1.1 S4.4.1.2): the authorization decision rests on a client-asserted JWT claim at `api/orders.py:84`" is.
- **Decide systemic or local before writing**: twelve instances of one missing convention is a single systemic finding, not twelve local ones. Filing them separately inflates the finding count and points remediation at the symptoms.
- **Quantify expected improvement against a named attribute**: readers prioritize by score lift, and a bare "+X.X points" does not tell them which quality improves.
- **Verification must be concrete**: "review again in 6 months" is not verification. "After fix: structured log `note.update` with `actor` and `outcome` appears for every PUT to `/notes/{id}`; the existing test `test_audit_emits_actor` passes" is.
