Look up the FIASSE/SSEM reference material for the specified topic and provide a concise explanation with practical guidance.

Reference `data/fiasse/` sections to find the relevant content. Each section file has YAML frontmatter with `when_to_use` triggers that help match the query.

## SSEM Quick Reference

| **Maintainability** | **Trustworthiness** | **Reliability** |
|:---------------------|:--------------------:|----------------:|
| Analyzability (S3.2.1.1) | Confidentiality (S3.2.2.1) | Availability (S3.2.3.1) |
| Modifiability (S3.2.1.2) | Accountability (S3.2.2.2) | Integrity (S3.2.3.2) |
| Testability (S3.2.1.3) | Authenticity (S3.2.2.3) | Resilience (S3.2.3.3) |

## Section Index

- S2.1–S2.6: Foundational Principles
- S3.1: SSEM Overview
- S3.2.1–S3.2.3: SSEM Attributes (Maintainability, Trustworthiness, Reliability)
- S3.3.1–S3.3.2: Transparency & Trust Boundaries
- S3.4.1–S3.4.3: Measurement
- S4.1–S4.4: Practical Implementation
- S5.1–S5.2: Organizational Integration
- S6.1–S6.5: Defensive Coding & Input Handling
- S7.0–S7.3: AI & Automation
- S8.1–S8.2: Conclusion & Future Work

## Arguments

- `$ARGUMENTS` — The FIASSE/SSEM topic to look up (e.g., "integrity", "trust boundaries", "input validation", "transparency", "S3.2.2").
