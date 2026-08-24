# FIASSE / SSEM Reference Data

88 structured FIASSE section files sourced from the [FIASSE framework v1.1](https://github.com/OWASP/FIASSE/blob/v1.1/docs/securable_framework.md) by Alton Crossley.

FIASSE (Framework for Integrating Application Security into Software Engineering) provides the overarching strategic approach. SSEM (Securable Software Engineering Model) provides the design language with **10 core attributes** grouped into 3 pillars: Maintainability, Trustworthiness, and Reliability.

## Source & License

These files are derived from the [OWASP/FIASSE](https://github.com/OWASP/FIASSE) repository at tag `v1.1`. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## File Format

Each file has YAML frontmatter with:

```yaml
---
title: "S3.2.1 Maintainability"
fiasse_section: "S3.2.1"
fiasse_version: "1.1"
ssem_pillar: "Maintainability"             # (optional) SSEM pillar
ssem_attributes:                           # (optional) SSEM sub-attributes
  - Analyzability
  - Modifiability
  - Testability
  - Observability
when_to_use:                               # Task-matching triggers
  - reviewing code for maintainability
  - assessing analyzability of a codebase
threats:                                   # Security implications addressed
  - undetected vulnerabilities due to complex code
  - slow vulnerability remediation
summary: "Definitions and contributing factors for Maintainability sub-attributes."
---
```

Followed by the FIASSE section content. Measurement sections (Appendix A, files `SA.*.md`) include tables:

```
| Metric | Type | Description |
| --- | --- | --- |
| Volume (LoC) | Quantitative | Overall size of the codebase |
```

## SSEM Model Reference (v1.1)

| **Maintainability** | **Trustworthiness** | **Reliability** |
|:--------------------|:-------------------:|----------------:|
| Analyzability       | Confidentiality     | Availability    |
| Modifiability       | Accountability      | Integrity       |
| Testability         | Authenticity        | Resilience      |
| Observability       |                     |                 |

The ten attributes are unchanged from v1.0.4. What changed in v1.1 is the guidance around them:

- **S2.4 The Quality-Security Relationship** is new, and shifts Aligning Security with Development to S2.5, the Transparency Principle to S2.6 (with new leaves S2.6.1–S2.6.3), and the Principle of Least Astonishment to S2.7.
- **S4.4.1.1** is renamed and reframed from "The Request Surface Minimization Principle" to **The Canonical Parsing Principle** — "parse, don't validate," with the parsed structure serving as proof that invariants hold.
- **S4.4.1.2** is renamed from "The Derived Integrity Principle" to **The Isolated Integrity Principle**, framed as isolation of *authority*.
- **S5.2.1–S5.2.5** define the **Securability Report**: generated on every merge, advisory by default, with gating as a policy decision and the resulting audit trail as compliance evidence.
- **S6.1** is new (Security Controls in the Code Creation Process, with the Control-as-Requirement and Control-as-Protection fallacies), shifting Shoveling Left to S6.2 and Strategic Use of Security Output to S6.3.
- **S7.1.1–S7.1.5** and **S8.1–S8.2** expand the security-team role and organizational adoption guidance.
- **SA.4 Scoring and Enhancement Suggestions** is new, and governs how composite SSEM scores may be presented.

S4.5 (Dependency Management) and S4.6 (Dependency Stewardship) remain separate sections in v1.1.

## Usage in Skills

### Securability Engineering Review (`/securability-review`)

When scoring SSEM attributes, reference the specific section for definitions and measurement criteria. Leaf attribute files give granular lookups:

```markdown
- **FIASSE Ref**: S3.2.1.1 Analyzability (definition + contributing factors)
- **Measurement**: SA.1.1 Measuring Analyzability (metrics + qualitative checks)
- **Scoring conduct**: SA.4 Scoring and Enhancement Suggestions
```

`SA.4` is the governing section for any composite score the review emits: the score is a directional management aid, never a statement of assurance, and it must ship with rationale and prioritized changes.

### FIASSE Code Analysis

When identifying code-level threats, apply the "What can go wrong?" framework (Section 4.2.1) and map identified issues to the relevant SSEM attributes and FIASSE sections for context and remediation guidance.

Use `when_to_use` frontmatter to match tasks to relevant FIASSE sections. For example, when reviewing dependency management:
- `S4.5` — Dependency Management
- `S4.6` — Dependency Stewardship (ongoing relationship)

### Task-Based Lookup

Use the `when_to_use` and `ssem_attributes` frontmatter to match analysis tasks to relevant sections. Leaf files (e.g., `S3.2.1.4.md` Observability) carry attribute-specific metadata for finer-grained matching.

## Section Index

| Section | Topic | Files |
|---------|-------|-------|
| §1 | Introduction | S1.1–S1.2 |
| §2 | Foundational Principles | S2.1–S2.7 (incl. S2.6.1–S2.6.3) |
| §3.1 | Model Overview and Design Language | S3.1 |
| §3.2 | Core Securable Attributes | S3.2, S3.2.1–S3.2.3 (umbrella + leaf) |
| §4 | Practical Guidance | S4.1–S4.6 (with leaf subsections) |
| §5 | Integrating Security into Dev Processes | S5.1–S5.3 (incl. S5.2.1–S5.2.5) |
| §6 | Common AppSec Anti-Patterns | S6.1–S6.3 (with leaf subsections) |
| §7 | Roles & Responsibilities | S7.1–S7.4 (incl. S7.1.1–S7.1.5) |
| §8 | Organizational Adoption of FIASSE | S8, S8.1–S8.2 (with leaf subsections) |
| Appendix A | Measuring SSEM Attributes | SA.1–SA.4 (with attribute leaves) |

## Detailed File Listing

| File | Title |
|------|-------|
| S1.1.md | The Application Security Challenge |
| S1.2.md | Document Purpose and Scope |
| S2.1.md | The Securable Paradigm: No Static Secure State |
| S2.2.md | Resiliently Add Computing Value |
| S2.3.md | Security Mission: Reducing Material Impact |
| S2.4.md | The Quality-Security Relationship |
| S2.5.md | Aligning Security with Development |
| S2.6.md | The Transparency Principle |
| S2.6.1.md | Transparency and Maintainability |
| S2.6.2.md | Transparency and Trustworthiness |
| S2.6.3.md | Transparency Tactics |
| S2.7.md | The Principle of Least Astonishment |
| S3.1.md | Model Overview and Design Language |
| S3.2.md | Core Securable Attributes |
| S3.2.1.md | Maintainability |
| S3.2.1.1.md | Analyzability |
| S3.2.1.2.md | Modifiability |
| S3.2.1.3.md | Testability |
| S3.2.1.4.md | Observability |
| S3.2.2.md | Trustworthiness |
| S3.2.2.1.md | Confidentiality |
| S3.2.2.2.md | Accountability |
| S3.2.2.3.md | Authenticity |
| S3.2.3.md | Reliability |
| S3.2.3.1.md | Availability |
| S3.2.3.2.md | Integrity |
| S3.2.3.3.md | Resilience |
| S4.1.md | Establishing Clear Expectations |
| S4.1.1.md | Proactive Communication |
| S4.1.2.md | Integrating Security into Requirements |
| S4.2.md | Threat Modeling |
| S4.2.1.md | Code-Level Threat Awareness |
| S4.2.2.md | Threat Modeling Solution Framework |
| S4.3.md | The Boundary Control Principle |
| S4.4.md | Resilient Coding |
| S4.4.1.md | Canonical Input Handling |
| S4.4.1.1.md | The Canonical Parsing Principle |
| S4.4.1.2.md | The Isolated Integrity Principle |
| S4.5.md | Dependency Management |
| S4.6.md | Dependency Stewardship |
| S5.1.md | Natively Extending Development Processes |
| S5.2.md | The Role of Merge Reviews |
| S5.2.1.md | The Securability Report |
| S5.2.2.md | The Advisory Default |
| S5.2.3.md | Gating as a Policy Decision |
| S5.2.4.md | The Audit Trail |
| S5.2.5.md | Posture over Pass Rates |
| S5.3.md | Early Integration: Planning and Requirements |
| S6.1.md | Security Controls in the Code Creation Process |
| S6.1.1.md | The Control-as-Requirement Fallacy |
| S6.1.2.md | The Control-as-Protection Fallacy |
| S6.1.3.md | The Requirements Process as the Corrective |
| S6.2.md | The Shoveling Left Phenomenon |
| S6.2.1.md | Ineffective Vulnerability Reporting |
| S6.2.2.md | Pitfalls of Exploit-First Training |
| S6.3.md | Strategic Use of Security Output |
| S7.1.md | The Role of the Security Team |
| S7.1.1.md | The Strategic Case for the Shift |
| S7.1.2.md | Capacity Relief Through Agentic AppSec |
| S7.1.3.md | Transition, Not Switchover |
| S7.1.4.md | Business-Leadership Alignment Is a Precondition |
| S7.1.5.md | Staffing Implications |
| S7.2.md | Senior Software Engineers |
| S7.3.md | Developing Software Engineers |
| S7.4.md | Product Owners and Managers |
| S8.md | Organizational Adoption of FIASSE |
| S8.1.md | Degraded-Mode Adoption |
| S8.1.1.md | Compensate with Agentic Assistance |
| S8.1.2.md | Invest in the Prerequisite First |
| S8.1.3.md | Adopt Partially with Named Gaps |
| S8.2.md | Indicators of Adoption Effectiveness |
| S8.2.1.md | Leading Indicators |
| S8.2.2.md | Lagging Indicators |
| S8.2.3.md | Distinguishing Framework Failure from Adoption Failure |
| SA.1.md | Measuring Maintainability |
| SA.1.1.md | Measuring Analyzability |
| SA.1.2.md | Measuring Modifiability |
| SA.1.3.md | Measuring Testability |
| SA.1.4.md | Measuring Observability |
| SA.2.md | Measuring Trustworthiness |
| SA.2.1.md | Measuring Confidentiality |
| SA.2.2.md | Measuring Accountability |
| SA.2.3.md | Measuring Authenticity |
| SA.3.md | Measuring Reliability |
| SA.3.1.md | Measuring Availability |
| SA.3.2.md | Measuring Integrity |
| SA.3.3.md | Measuring Resilience |
| SA.4.md | Scoring and Enhancement Suggestions |

## Updating

To refresh from upstream:

```bash
# Fetch the v1.1 framework
curl -o /tmp/securable_framework.md https://raw.githubusercontent.com/OWASP/FIASSE/refs/tags/v1.1/docs/securable_framework.md
# Extract sections using the extraction script
python scripts/extract_fiasse_sections.py /tmp/securable_framework.md data/fiasse/
```

Pin the fetch to a released tag. Extracting from unreleased upstream `main` will pull in section numbering that has not shipped — for example, the consolidation of S4.5 and S4.6 into a single section.
