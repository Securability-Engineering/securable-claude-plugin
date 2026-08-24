---
name: fiasse-lookup
description: Answer questions about FIASSE v1.1 and SSEM from the bundled framework reference — definitions, principles (Securable Paradigm, Boundary Control, Canonical Parsing, Isolated Integrity, Transparency, Least Astonishment), the ten SSEM attributes, scoring conduct (SA.4), merge-review guidance (S5.2), and section lookups by number (e.g. "S4.4.1.2"). Trigger on "what does FIASSE say about…", "explain SSEM/securability/securable", "define <attribute>", or any FIASSE/SSEM section reference. Answer from the bundled data, citing section numbers — not from memory.
license: CC-BY-4.0
---

# FIASSE / SSEM Reference Lookup

Look up the FIASSE/SSEM reference material for the specified topic and provide a concise explanation with practical guidance.

> **Path resolution**: every `data/` path in this skill lives at the plugin root — the directory two levels above this SKILL.md file. In a Claude Code plugin install that root is `${CLAUDE_PLUGIN_ROOT}`; in a repo checkout or a copied skills tree, resolve relative to this file (e.g., `../../data/fiasse/S2.1.md`). These paths never refer to the user's project.

Reference `data/fiasse/` sections to find the relevant content. Each section file has YAML frontmatter (including `fiasse_version: 1.1`) with `when_to_use` triggers that help match the query. Ground every answer in the section text — open the file and cite the section number rather than answering from memory.

## SSEM Quick Reference (FIASSE v1.1 — 10 attributes)

| **Maintainability** | **Trustworthiness** | **Reliability** |
|:--------------------|:-------------------:|----------------:|
| Analyzability (S3.2.1.1) | Confidentiality (S3.2.2.1) | Availability (S3.2.3.1) |
| Modifiability (S3.2.1.2) | Accountability (S3.2.2.2) | Integrity (S3.2.3.2) |
| Testability (S3.2.1.3)   | Authenticity (S3.2.2.3)   | Resilience (S3.2.3.3) |
| Observability (S3.2.1.4) |                           |                       |

> SSEM has no Authorization attribute by design (S3.2.2.3). Authorization is a security *feature*, gathered as a requirement and implemented against acceptance criteria. Authenticity, Confidentiality, Integrity, and Accountability are what make it defensible.

## Section Index (FIASSE v1.1)

- **S1.1–S1.2** — Introduction (challenge, purpose, scope)
- **S2.1–S2.7** — Foundational Principles: Securable Paradigm (S2.1), Resiliently Add Computing Value (S2.2), Reducing Material Impact (S2.3), Quality-Security Relationship (S2.4), Aligning Security with Development (S2.5), Transparency (S2.6 + leaves S2.6.1–S2.6.3), Least Astonishment (S2.7)
- **S3.1** — SSEM Model Overview and Design Language
- **S3.2** — Core Securable Attributes (umbrella)
- **S3.2.1** — Maintainability + leaves (S3.2.1.1 Analyzability, S3.2.1.2 Modifiability, S3.2.1.3 Testability, S3.2.1.4 Observability)
- **S3.2.2** — Trustworthiness + leaves (Confidentiality, Accountability, Authenticity)
- **S3.2.3** — Reliability + leaves (Availability, Integrity, Resilience)
- **S4.1–S4.6** — Practical Guidance: Clear Expectations (S4.1), Threat Modeling (S4.2), Boundary Control Principle (S4.3), Resilient Coding (S4.4) + Canonical Input Handling leaves (S4.4.1, S4.4.1.1 Canonical Parsing, S4.4.1.2 Isolated Integrity), Dependency Management (S4.5), Dependency Stewardship (S4.6)
- **S5.1–S5.3** — Integrating Security into Development Processes: Native extension (S5.1), Merge Reviews (S5.2 + leaves S5.2.1 Securability Report, S5.2.2 Advisory Default, S5.2.3 Gating as Policy, S5.2.4 Audit Trail, S5.2.5 Posture over Pass Rates), Early Integration (S5.3)
- **S6.1–S6.3** — Common AppSec Anti-Patterns: Security Controls in the Code Creation Process (S6.1 + leaves S6.1.1 Control-as-Requirement, S6.1.2 Control-as-Protection, S6.1.3 Requirements Process as Corrective), Shoveling Left (S6.2 + leaves), Strategic Use of Security Output (S6.3)
- **S7.1–S7.4** — Roles and Responsibilities: Security Team (S7.1 + leaves S7.1.1–S7.1.5), Senior Engineers (S7.2), Developing Engineers (S7.3), Product Owners (S7.4)
- **S8** — Organizational Adoption + Degraded-Mode Adoption (S8.1 + leaves) and Indicators of Adoption Effectiveness (S8.2 + leaves)
- **SA.1–SA.4** — Appendix A: Measuring SSEM Attributes (Maintainability, Trustworthiness, Reliability) with attribute leaves (SA.1.4 measures Observability), plus **SA.4 Scoring and Enhancement Suggestions**

> **Renamed in v1.1**: "Request Surface Minimization" is now **Canonical Parsing** (S4.4.1.1); "Derived Integrity" is now **Isolated Integrity** (S4.4.1.2). If a query uses the old name, answer with the new one and note the rename.

## Query Handling

Accept a topic in any form — an attribute name ("integrity"), a concept ("trust boundaries", "least astonishment"), a section number ("S3.2.2"), or a question ("what does FIASSE say about scoring?"). Match it against the section index above and the `when_to_use` frontmatter, read the matching `data/fiasse/` file(s), and answer concisely with:

1. The definition or principle, in plain language
2. The section citation (e.g., FIASSE v1.1 S4.4.1.2)
3. One concrete engineering implication for the user's current context, when known
