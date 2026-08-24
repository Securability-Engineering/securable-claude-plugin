# Play: Securable Code Analysis (FIASSE v1.1 / SSEM)

Step-by-step runbook for executing an SSEM-scored review.

> **Source of truth**: [skills/securability-engineering-review/SKILL.md](../../skills/securability-engineering-review/SKILL.md) defines the rubric, equal attribute weights (1/10 each), the weakest-link floor, severity classification, output format, and the 50-item checklist. This play does not redefine them — it sequences the work.

## Trigger Conditions

Run this play when:

- Performing a proactive security posture assessment of a codebase (beyond vulnerability scanning)
- Evaluating code quality attributes that directly impact security outcomes
- Producing a Securability Report for a merge review (FIASSE v1.1 S5.2.1)
- Establishing a baseline of securable attributes for a project
- A user asks to assess code securability, code quality for security, or FIASSE/SSEM compliance

## Inputs

- Code files, modules, or full codebase to analyze
- (Optional) Architecture documentation or data-flow diagrams
- (Optional) Target attribute focus areas
- (Optional) Prior static-analysis or quality reports
- (Optional) Dependency manifests
- (Optional but strongly preferred) **Prior SSEM scorecard** — SA.4 asks for deltas against previous scans

## Steps

### 1. Establish scope and context

Capture before scoring:

- Language / framework
- System type (web app, API, library, CLI, agent, microservice)
- Data sensitivity (PII, credentials, financial, health, regulated)
- Exposure (internet-facing, internal, local-only)
- Lifecycle stage (new, mature, legacy under maintenance)
- Team context (size, experience, velocity)
- Prior baseline score, if one exists

Without this, scores are guesses.

### 2. Apply triage and sampling (large codebases only)

For codebases beyond a few thousand LoC, follow the triage strategy in the skill: trust boundaries first, then security-sensitive modules, data-access layer, architectural seams, cross-cutting infrastructure, and a small spot-sample of business logic.

Mark every sampled path in the report. Where an attribute's evidence lies entirely in code you did not open, mark that attribute **`Not assessed`** — do not assign it a number. Past two `Not assessed` attributes, the report carries no overall score.

### 3. Inspect the code, not the docs

Open files. Trace flows. Sample tests. Rubric anchors are about what *is* there, not what is *claimed*.

### 4. Score Maintainability (4 attributes)

Score each on the skill's 0-10 anchor scale, citing file paths or patterns:

- **Analyzability** (FIASSE v1.1 S3.2.1.1) — clarity, complexity, naming, structure
- **Modifiability** (FIASSE v1.1 S3.2.1.2) — coupling, cohesion, separation of concerns, no static mutable state
- **Testability** (FIASSE v1.1 S3.2.1.3) — coverage of security-critical paths, mockability, independence
- **Observability** (FIASSE v1.1 S3.2.1.4) — log coverage at boundaries, code-level instrumentation, failure-path visibility

### 5. Score Trustworthiness (3 attributes)

- **Confidentiality** (FIASSE v1.1 S3.2.2.1) — secrets, PII handling, least privilege, encryption at rest/in transit
- **Accountability** (FIASSE v1.1 S3.2.2.2) — audit-trail completeness, structured logging, action traceability
- **Authenticity** (FIASSE v1.1 S3.2.2.3) — auth mechanisms, token integrity, credential lifecycle, non-repudiation

Authorization is not an SSEM attribute (S3.2.2.3). Score the attributes a sound authorization feature depends on, and treat a missing authorization requirement as a requirements finding (S6.1.1), not a missing attribute.

### 6. Score Reliability (3 attributes)

- **Availability** (FIASSE v1.1 S3.2.3.1) — resource limits, timeouts, rate limiting, graceful degradation
- **Integrity** (FIASSE v1.1 S3.2.3.2) — Canonical Parsing (S4.4.1.1), Isolated Integrity (S4.4.1.2), parameterized queries, output encoding
- **Resilience** (FIASSE v1.1 S3.2.3.3) — specific exception handling, defensive coding, deterministic disposal, graceful and secure failure

### 7. Apply pattern tagging

For each weakness, name the principle violated using the **Pattern Tag Reference** in the skill. "Isolated Integrity violation (FIASSE v1.1 S4.4.1.2)" is actionable; "the auth is sketchy" is not.

### 8. Classify each finding systemic or local

A pattern that is the codebase's default is one **systemic** finding, however many times it appears; cite representative sites and state the count. A one-off deviation from an otherwise sound practice is **local**. Filing systemic issues as N local findings inflates the count and points remediation at symptoms (FIASSE v1.1 SA.4, S6.2).

### 9. Apply the Four-Question Framework at the code level (FIASSE v1.1 S4.2.1)

Use static-analysis findings as starting points, then think deeper:

1. What are we building?
2. What can go wrong?
3. What are we going to do about it?
4. Did we do a good job?

Map solutions back to SSEM attributes — prefer architectural fixes over line-level patches when the same root cause produces multiple findings.

### 10. Assess dependency stewardship

Per FIASSE v1.1 S4.5 (Dependency Management) and S4.6 (Dependency Stewardship), evaluate:

- Documented rationale for inclusion
- Pinned versions / lockfiles
- Known transitive dependencies
- Maintenance signals (release cadence, maintainer activity, CVE response)
- Whether the dependency would remain trustworthy a year from now (Stewardship)

### 11. Compute scores

- **Raw mean** = mean of all assessed attribute scores (equal weight, 1/10 each)
- **Floor** = lowest assessed attribute score + 3.0
- **Overall** = min(raw mean, floor)

Report the raw mean, the floor, which constraint binds, and the weakest attribute by name. Compute pillar means as **diagnostics only** — they show which family of qualities is weak and never feed the overall score. Show the math in the report.

### 12. Classify each finding's severity

Use the severity table in the skill — engineering-impact based, expressed in **attribute points**, not CVSS and not pillar points. Severities are CRITICAL / HIGH / MEDIUM / LOW / INFO.

### 13. Assemble the three-part report

Use the output format and checklist defined in the skill:

- **Part 1**: SSEM Score Summary (SA.4 framing line, overall with math, delta vs baseline, attribute table, pillar diagnostics, top 3 strengths, top 3 improvements)
- **Part 2**: Detailed Findings per pillar (use [templates/finding.md](../../templates/finding.md) for individual findings)
- **Part 3**: 50-item Evaluation Checklist (5 per attribute)

Use [templates/report.md](../../templates/report.md) as the assembly scaffold.

### 14. Frame the result honestly

Per FIASSE v1.1 SA.4, close with the score, the rationale, and a short list of prioritized changes — and state that the score is a directional aid, not an assurance verdict. Where the system is high-impact or the score dropped materially against the baseline, flag that a reviewer should confirm the recommendations before they become development commitments.

## Quality Gates

- [ ] Scope, language, exposure, and prior baseline captured before scoring
- [ ] Sampling discipline declared (file paths inspected; un-inspected attributes marked `Not assessed`)
- [ ] Every one of the 10 attributes has a 0-10 score, `Not assessed`, or a justified `N/A`, each with code-anchored evidence
- [ ] No overall score emitted if more than 2 attributes are `Not assessed`
- [ ] Overall-score math shown: raw mean, floor, binding constraint, weakest attribute
- [ ] Pillar means labelled as diagnostics, not as score inputs
- [ ] Every weakness tagged to a FIASSE v1.1 principle where applicable
- [ ] Every finding tagged systemic or local
- [ ] Severity assigned to every finding, in attribute points
- [ ] Every expected improvement expressed as "+X.X on [Attribute]"
- [ ] Delta against prior baseline reported, or absence of a baseline stated
- [ ] SA.4 framing line present
- [ ] 50-item checklist completed with inline notes on failing items

## References

- [skills/securability-engineering-review/SKILL.md](../../skills/securability-engineering-review/SKILL.md) — rubric, weights, scoring math, severity, output format, 50-item checklist, pattern tags, anti-patterns
- [templates/finding.md](../../templates/finding.md) — individual finding shape
- [templates/report.md](../../templates/report.md) — full-report scaffold
- [FIASSE Framework v1.1](https://github.com/OWASP/FIASSE/blob/v1.1/docs/securable_framework.md)
- FIASSE v1.1 SA.4 — Scoring and Enhancement Suggestions (`data/fiasse/SA.4.md`)
- FIASSE v1.1 S5.2.1–S5.2.5 — The Securability Report (`data/fiasse/S5.2.*.md`)
- ISO/IEC 25010:2011 — Software quality models
- ISO/IEC 5055 — Structural quality measures from source code
- RFC 4949 — Internet Security Glossary
