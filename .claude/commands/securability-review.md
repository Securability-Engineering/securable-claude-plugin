Analyze the code in this project (or the specified files/directories) for securable engineering qualities using the FIASSE/SSEM framework.

Follow the full procedure in `plays/code-analysis/securability-engineering-review.md`.
Use the skill definition in `skills/securability-engineering-review/SKILL.md` for the rubric, scoring math, grading scale, and severity classification.
Reference `data/fiasse/` sections for attribute definitions and measurement criteria.

## Steps

1. **Scope & Context** — Determine language/framework, system type, data sensitivity, exposure, and trust boundaries for the target code. Ask for any prior SSEM scorecard so the report can show deltas (FIASSE v1.1 SA.4).

2. **SSEM Assessment** — Score all **ten** FIASSE v1.1 SSEM attributes, 0-10 each, at equal weight (1/10):
   - **Maintainability**: Analyzability (S3.2.1.1), Modifiability (S3.2.1.2), Testability (S3.2.1.3), Observability (S3.2.1.4)
   - **Trustworthiness**: Confidentiality (S3.2.2.1), Accountability (S3.2.2.2), Authenticity (S3.2.2.3)
   - **Reliability**: Availability (S3.2.3.1), Integrity (S3.2.3.2), Resilience (S3.2.3.3)

   Where evidence was not inspected, mark the attribute `Not assessed` rather than guessing a number. Where an attribute has no surface in this system, mark it `N/A` with a justification. Both are excluded from the mean; more than two `Not assessed` attributes means no overall score is emitted.

3. **Transparency & Observability Assessment** — Evaluate logging, audit trails, and code-level instrumentation (FIASSE v1.1 S2.6 Transparency, S3.2.1.4 Observability), and Least Astonishment in interfaces (S2.7).

4. **Code-Level Threat Identification** — Apply the Four Question Framework: "What can go wrong?" Map solutions to SSEM attributes, and tag each finding systemic or local.

5. **Compute the Score** — raw mean of assessed attributes; floor = lowest attribute + 3.0; overall = min(raw mean, floor). Report the raw mean, the floor, which constraint binds, and the weakest attribute by name. Pillar means are reported as diagnostics only and never feed the overall score.

6. **Produce Report** — Generate the full report using `templates/report.md` format, with individual findings using `templates/finding.md` format. Include the SA.4 framing line, the SSEM Score Summary, detailed findings per pillar, and the 50-item evaluation checklist (5 per attribute).

## Scoring Conduct

Per FIASSE v1.1 SA.4, the composite score is a directional management aid — useful for comparing this system against itself over time and for surfacing the weakest attribute first. It is **not** a statement of assurance, compliance, or security. Say so in the report, and pair every score with its rationale and a short list of prioritized changes.

## Arguments

- `$ARGUMENTS` — Files, directories, or components to analyze. If empty, analyze the entire project.
