# SSEM Assessment Report Template

Use this scaffold to assemble the three-part output of the `securability-engineering-review` skill, or the baseline / delta / post-enhancement report from the end-to-end securable generation play.

The skill at [skills/securability-engineering-review/SKILL.md](../skills/securability-engineering-review/SKILL.md) is the source of truth for the rubric (FIASSE v1.1 — 10 attributes, equal attribute weights, weakest-link floor), severity classification, and the 50-item checklist below. This template only supplies the structural shape.

Scoring conduct is governed by FIASSE v1.1 SA.4: the score is a directional management aid, not a statement of assurance or compliance.

````markdown
# SSEM Assessment Report — [Project Name]

**Date**: YYYY-MM-DD
**Scope**: [What was assessed — repo / service / module / merge request / changeset]
**Language / Framework**: [...]
**Exposure**: [internet-facing | internal | local-only]
**Lifecycle Stage**: [new | mature | legacy]
**Sampling Discipline**: [comprehensive | sampled — list the file paths actually inspected; attributes whose evidence was not inspected are marked `Not assessed`]
**Prior Baseline**: [date + overall score of the previous scorecard, or "none — this is the first"]

> This is an SSEM securability scorecard. Per FIASSE v1.1 SA.4, the score is a
> directional management aid for comparing this system against itself over time
> and for surfacing its weakest attribute first. It is not a statement of
> assurance, compliance, or security, and it should not be read as a verdict.

---

## Part 1 — SSEM Score Summary

### Overall

- **Raw mean** (all assessed attributes): [X.X]
- **Floor** (lowest attribute [X] + 3.0): [X.X]
- **Overall SSEM Score**: [X.X] / 10 — binding constraint: **[raw mean | floor]**
- **Weakest attribute**: [Name] at [X]
- **Grade**: Exemplary | Strong | Adequate | Weak | Minimal | Absent
- **Status**: [one-line assessment]

[If the floor is binding, say so here in one sentence: the mean would have read
[X.X] ([Grade]), and the floor is what prevents [weakest attribute] from being
averaged away.]

[If more than 2 attributes are `Not assessed`, omit every figure above and state:
"Coverage is too thin for a composite score — N of 10 attributes were not
assessed. Attribute detail follows; no overall score is emitted."]

### Delta Against Prior Baseline

| Attribute | Prior | Current | Δ |
| --- | --- | --- | --- |
| [Attribute] | [X.X] | [X.X] | [+/-X.X] |
| **Overall** | **[X.X]** | **[X.X]** | **[+/-X.X]** |

[Or: "No prior scorecard exists for this system. This report establishes the baseline."]

### Attribute Scores

All ten attributes carry equal weight (10% each). `Not assessed` and `N/A` are excluded from the mean and the floor.

| Attribute | Pillar | Weight | Score | Grade | Assessment |
| --- | --- | --- | --- | --- | --- |
| Analyzability (FIASSE v1.1 S3.2.1.1) | Maintainability | 10% | [X]/10 | [Grade] | [brief] |
| Modifiability (FIASSE v1.1 S3.2.1.2) | Maintainability | 10% | [X]/10 | [Grade] | [brief] |
| Testability (FIASSE v1.1 S3.2.1.3) | Maintainability | 10% | [X]/10 | [Grade] | [brief] |
| Observability (FIASSE v1.1 S3.2.1.4) | Maintainability | 10% | [X]/10 | [Grade] | [brief] |
| Confidentiality (FIASSE v1.1 S3.2.2.1) | Trustworthiness | 10% | [X]/10 | [Grade] | [brief] |
| Accountability (FIASSE v1.1 S3.2.2.2) | Trustworthiness | 10% | [X]/10 | [Grade] | [brief] |
| Authenticity (FIASSE v1.1 S3.2.2.3) | Trustworthiness | 10% | [X]/10 | [Grade] | [brief] |
| Availability (FIASSE v1.1 S3.2.3.1) | Reliability | 10% | [X]/10 | [Grade] | [brief] |
| Integrity (FIASSE v1.1 S3.2.3.2) | Reliability | 10% | [X]/10 | [Grade] | [brief] |
| Resilience (FIASSE v1.1 S3.2.3.3) | Reliability | 10% | [X]/10 | [Grade] | [brief] |

Use `Not assessed` (with the coverage gap named) or `N/A` (with a justification for why the attribute has no surface in this system) in place of a score where appropriate.

**Math**: raw mean = sum of assessed scores / count of assessed = [X.X]. Floor = [lowest] + 3.0 = [X.X]. Overall = min([X.X], [X.X]) = **[X.X]**.

### Pillar Diagnostics

Pillar means are reported to show which family of qualities is weak. They are **not** inputs to the overall score.

| Pillar | Diagnostic Mean | Grade | Key Finding |
| --- | --- | --- | --- |
| Maintainability | [X.X] / 10 | [Grade] | [one-line key finding] |
| Trustworthiness | [X.X] / 10 | [Grade] | [one-line key finding] |
| Reliability | [X.X] / 10 | [Grade] | [one-line key finding] |

### Top 3 Strengths

1. [Strength with concrete evidence — file path, pattern name, or short quote]
2. [Strength with concrete evidence]
3. [Strength with concrete evidence]

### Top 3 Improvement Opportunities

Ordered by attribute impact. Lead with whatever the floor is binding on.

1. [Weakness + concrete recommendation] — *+[X.X] on [Attribute]*
2. [Weakness + concrete recommendation] — *+[X.X] on [Attribute]*
3. [Weakness + concrete recommendation] — *+[X.X] on [Attribute]*

### Review Flag

[Where the system is high-impact, or the overall score dropped materially against
the prior baseline, state that a reviewer should confirm these recommendations
before they become development commitments (FIASSE v1.1 SA.4). Otherwise omit.]

---

## Part 2 — Detailed Findings

### Maintainability — diagnostic mean [X.X]/10 ([Grade])

**Strengths**
- [Specific strength with file:line or pattern]
- [Another strength]

**Weaknesses**
- [Specific weakness with location and impact note]
- [Another weakness]

**Recommendations**

1. **[Title]** (Severity: CRITICAL | HIGH | MEDIUM | LOW | INFO — Systemic | Local)
   - Issue: [Specific problem]
   - Impact: [Effect on the named attribute and on the system]
   - Solution: [Actionable steps]
   - Expected Improvement: +[X.X] on [Attribute]

[Add additional recommendations as needed.]

### Trustworthiness — diagnostic mean [X.X]/10 ([Grade])

[Same shape as Maintainability above.]

### Reliability — diagnostic mean [X.X]/10 ([Grade])

[Same shape as Maintainability above.]

### Individual Findings

For each finding, use the format defined in [finding.md](finding.md). Findings name the SSEM pillar and attribute, the FIASSE v1.1 reference, the pattern tag, whether the issue is systemic or local, location, current state, evidence, impact, remediation, expected improvement, verification, and confidence.

---

## Part 3 — Appendix A: Evaluation Checklist (50 items)

Five items per attribute across all ten attributes — the same 1/10 weighting the score uses. Mark each `[x]` (passing) or `[ ]` (failing) with a brief inline note when failing. Mark `[-]` for items belonging to an attribute scored `Not assessed` or `N/A`, and exclude them from the denominator.

### Maintainability (20 items)

**Analyzability**
- [ ] Methods under 30 lines
- [ ] Cyclomatic complexity < 10
- [ ] Clear, descriptive naming
- [ ] Self-documenting code; comments only at trust boundaries / complex logic
- [ ] No dead code or commented-out blocks

**Modifiability**
- [ ] Loose coupling with clear interfaces
- [ ] No static mutable state
- [ ] Security-sensitive logic centralized (auth, crypto, boundary parsing)
- [ ] Configuration externalized
- [ ] Dependency injection (or equivalent) enables component replacement

**Testability**
- [ ] Security-critical paths have dedicated test suites
- [ ] Negative / boundary / malicious-input cases covered
- [ ] Tests run without external dependencies (clean mocking)
- [ ] Test execution fast enough for every commit
- [ ] Integration tests cover trust-boundary crossings

**Observability**
- [ ] Structured logs include who, what, where, when, outcome at security-relevant events
- [ ] Failure paths produce log/metric output (no silent failures)
- [ ] Code-level instrumentation at trust boundaries (not external tooling alone)
- [ ] Health and performance metrics exposed via standardized API
- [ ] UI/operator feedback surfaces meaningful state without leaking internals

### Trustworthiness (15 items)

**Confidentiality**
- [ ] Sensitive data types identified and classified
- [ ] Least-privilege data access
- [ ] Encryption at rest for sensitive data
- [ ] Encryption in transit enforced
- [ ] No secrets / PII / tokens in code, logs, or error messages

**Accountability**
- [ ] Security-sensitive actions logged with structured data (who/what/where/when)
- [ ] Audit trails immutable or append-only
- [ ] Authentication events recorded (login, logout, failure)
- [ ] Authorization decisions logged (grant, deny)
- [ ] Permission / config changes captured with actor and outcome

**Authenticity**
- [ ] Authentication uses established, strong mechanisms (MFA where appropriate)
- [ ] Token / session integrity verified (signed JWTs with pinned alg, secure cookies)
- [ ] Service-to-service calls mutually authenticated
- [ ] Data origin verifiable where applicable (signatures, checksums)
- [ ] Credential and token lifecycles support rotation, expiry, and revocation

### Reliability (15 items)

**Availability**
- [ ] Resource limits enforced (memory, connections, file handles)
- [ ] Timeouts configured for all external calls
- [ ] Rate limiting protects against resource exhaustion
- [ ] Thread-safe design where concurrency is used
- [ ] Graceful degradation for non-critical failures

**Integrity**
- [ ] Input canonicalized → sanitized → validated at every trust boundary (FIASSE v1.1 S4.4.1)
- [ ] Output-encoded when crossing trust boundaries
- [ ] Database operations use parameterized queries exclusively
- [ ] Isolated Integrity applied — integrity-critical values derived from server-side authority, never accepted from the client (FIASSE v1.1 S4.4.1.2)
- [ ] Canonical Parsing applied — boundary input parsed into a typed structure against an explicit per-operation schema, failing closed (FIASSE v1.1 S4.4.1.1)

**Resilience**
- [ ] Specific exception handling (no bare catch-all) with meaningful messages
- [ ] Defensive coding anticipates out-of-bounds input
- [ ] Null confined to input and DB boundaries; absence represented explicitly in business logic
- [ ] No resource leaks; deterministic disposal patterns (`with`, `using`, RAII)
- [ ] Graceful and **secure** failure — error messages do not leak internals

### Checklist Summary

- Maintainability: N/20 passing (NN%)
- Trustworthiness: N/15 passing (NN%)
- Reliability: N/15 passing (NN%)
- **Overall: N/50 passing (NN%)**

### Severity Summary

- CRITICAL: N
- HIGH: N
- MEDIUM: N
- LOW: N
- INFO: N

### Systemic vs Local

- Systemic findings: N
- Local findings: N

[Where systemic findings dominate, note that remediation is a convention or
architectural change, not N separate fixes.]
````

## Optional: Baseline / Delta / Post-Enhancement Sections

When this report is the artifact of the end-to-end securable generation play (see [plays/code-generation/securable-generation.md](../plays/code-generation/securable-generation.md)), append:

````markdown
## Baseline vs Post-Enhancement

| Attribute | Baseline | Post-Enhancement | Δ |
| --- | --- | --- | --- |
| Analyzability | [X.X] | [X.X] | [+/-X.X] |
| Modifiability | [X.X] | [X.X] | [+/-X.X] |
| Testability | [X.X] | [X.X] | [+/-X.X] |
| Observability | [X.X] | [X.X] | [+/-X.X] |
| Confidentiality | [X.X] | [X.X] | [+/-X.X] |
| Accountability | [X.X] | [X.X] | [+/-X.X] |
| Authenticity | [X.X] | [X.X] | [+/-X.X] |
| Availability | [X.X] | [X.X] | [+/-X.X] |
| Integrity | [X.X] | [X.X] | [+/-X.X] |
| Resilience | [X.X] | [X.X] | [+/-X.X] |
| **Raw mean** | [X.X] | [X.X] | [+/-X.X] |
| **Floor** | [X.X] | [X.X] | [+/-X.X] |
| **Overall** | **[X.X]** | **[X.X]** | **[+/-X.X]** |

Note which constraint binds before and after. Lifting the weakest attribute off
the floor often moves the overall score more than raising three strong ones.

## Implemented Enhancements

1. [Enhancement applied — file paths touched and pattern tag addressed]
2. [...]

## Residual Findings

For findings *not* fixed within the iteration cap, list them with severity, attribute, location, systemic/local, and an effort estimate so the team can plan follow-up.

## Next Recommendations

[Concise, prioritized list of next steps.]
````

## Notes

- Severity is engineering-impact based and expressed in **attribute points**; defined in [skills/securability-engineering-review/SKILL.md](../skills/securability-engineering-review/SKILL.md). Do not import CVSS, CWE, or CVE — those are assurance-tool concepts and are out of scope for an SSEM report.
- Sampling discipline is the report's credibility floor. Declare what was inspected; mark the rest `Not assessed` rather than assigning it a number.
- The overall-score math must be visible: raw mean, floor, and which constraint binds. Pillar means are diagnostics and never feed the overall score.
- Every expected improvement names its attribute. A bare "+X.X points" is not actionable.
