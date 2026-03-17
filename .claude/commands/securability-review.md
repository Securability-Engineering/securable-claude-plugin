Analyze the code in this project (or the specified files/directories) for securable engineering qualities using the FIASSE/SSEM framework.

Follow the full procedure in `plays/code-analysis/securability-engineering-review.md`.
Use the skill definition in `skills/securability-engineering-review/SKILL.md` for scoring weights, grading scale, and severity classification.
Reference `data/fiasse/` sections for attribute definitions and measurement criteria.

## Steps

1. **Scope & Context** — Determine language/framework, system type, data sensitivity, exposure, and trust boundaries for the target code.

2. **SSEM Assessment** — Score all nine attributes across three pillars:
   - **Maintainability**: Analyzability, Modifiability, Testability
   - **Trustworthiness**: Confidentiality, Accountability, Authenticity
   - **Reliability**: Availability, Integrity, Resilience

3. **Transparency Assessment** — Evaluate logging, audit trails, instrumentation, and observability.

4. **Code-Level Threat Identification** — Apply the Four Question Framework: "What can go wrong?" Map solutions to SSEM attributes.

5. **Produce Report** — Generate the full report using `templates/report.md` format, with individual findings using `templates/finding.md` format. Include the SSEM Score Summary, detailed findings per pillar, and the 45-item evaluation checklist.

## Arguments

- `$ARGUMENTS` — Files, directories, or components to analyze. If empty, analyze the entire project.
