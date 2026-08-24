#!/usr/bin/env python3
"""
Extract FIASSE framework sections (v1.1) into structured markdown files
with YAML frontmatter.

Parses the FIASSE framework markdown (from OWASP/FIASSE,
file `docs/securable_framework.md`) and produces one file per logical section
under data/fiasse/. Each output file has YAML frontmatter (title,
fiasse_section, ssem_pillar, ssem_attributes, when_to_use, threats, summary)
followed by the section content.

Section files are named S{x.y.z}.md (e.g. S3.2.1.4.md for Observability,
SA.1.4.md for the Appendix A measurement subsection).

Updated for FIASSE v1.1. Relative to v1.0.4, the v1.1 framework introduces:
  - The Quality-Security Relationship (new Section 2.4), which shifts
    Aligning Security with Development to 2.5, Transparency to 2.6, and the
    Principle of Least Astonishment to 2.7
  - Transparency subsections 2.6.1-2.6.3
  - "The Request Surface Minimization Principle" renamed and reframed as
    "The Canonical Parsing Principle" (Section 4.4.1.1), built on
    "parse, don't validate" and data-structure-as-proof
  - "The Derived Integrity Principle" renamed to
    "The Isolated Integrity Principle" (Section 4.4.1.2)
  - The Securability Report mechanism (Sections 5.2.1-5.2.5)
  - Security Controls in the Code Creation Process (new Section 6.1 with the
    Control-as-Requirement and Control-as-Protection fallacies), which shifts
    Shoveling Left to 6.2 and Strategic Use of Security Output to 6.3
  - Security-team role subsections 7.1.1-7.1.5
  - Degraded-Mode Adoption (8.1) and Indicators of Adoption Effectiveness (8.2)
  - Appendix A.4, Scoring and Enhancement Suggestions

Sections 4.5 (Dependency Management) and 4.6 (Dependency Stewardship) remain
separate in v1.1; they are consolidated only on unreleased upstream main.

Default upstream source:
  https://raw.githubusercontent.com/OWASP/FIASSE/refs/tags/v1.1/docs/securable_framework.md
"""

from __future__ import annotations

import re
import sys
import textwrap
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Section metadata registry
# ---------------------------------------------------------------------------
# Maps section_id -> metadata dict. Each entry defines the frontmatter fields
# that cannot be inferred from the framework text alone (when_to_use, threats,
# summary, and optionally ssem_pillar / ssem_attributes).

SECTION_META: dict[str, dict] = {
    # -----------------------------------------------------------------------
    # 1. Introduction
    # -----------------------------------------------------------------------
    "1.1": {
        "title": "The Application Security Challenge",
        "when_to_use": [
            "understanding why application security initiatives struggle",
            "framing the business case for securable code practices",
            "assessing friction between AppSec and Development teams",
            "evaluating the impact of generative AI on AppSec outcomes",
        ],
        "threats": [
            "slow progress in application security outcomes",
            "friction between AppSec and Development teams",
            "AI-generated code amplifying past security mistakes",
            "shift-left initiatives that fail to produce lasting change",
        ],
        "summary": (
            "The core challenge: organizations invest significantly in AppSec yet "
            "often see limited outcomes. Shift-left has underdelivered, AI code "
            "generation amplifies risk, and developers lack deep security expertise."
        ),
    },
    "1.2": {
        "title": "Document Purpose and Scope",
        "when_to_use": [
            "understanding the scope and audience of FIASSE",
            "distinguishing FIASSE from SSEM",
            "mapping FIASSE to organizational roles (AppSec, Product Security)",
            "introducing the term 'securable' versus 'secure'",
        ],
        "threats": [
            "misunderstanding the framework scope",
            "siloed security functions lacking a unifying framework",
        ],
        "summary": (
            "Defines FIASSE as the overarching strategic framework and SSEM as the "
            "design language model within it. Introduces the deliberate term "
            "'securable' over 'secure'."
        ),
    },
    # -----------------------------------------------------------------------
    # 2. Foundational Principles
    # -----------------------------------------------------------------------
    "2.1": {
        "title": "The Securable Paradigm: No Static Secure State",
        "when_to_use": [
            "explaining the difference between secure and securable",
            "challenging binary secure/insecure classification",
            "advocating for adaptive security posture",
            "applying the securable paradigm to features (e.g., Defendable Authentication)",
        ],
        "threats": [
            "treating security as a binary state",
            "brittle security that breaks when software changes",
            "failure to adapt to evolving threat landscape",
        ],
        "summary": (
            "There is no static state of secure. Software must be built with inherent "
            "qualities that enable it to adapt to evolving threats."
        ),
    },
    "2.2": {
        "title": "Resiliently Add Computing Value",
        "when_to_use": [
            "framing the primary directive of software engineering",
            "connecting security to business value creation",
            "justifying securable attributes as engineering requirements",
        ],
        "threats": [
            "software that cannot withstand change or stress",
            "security treated as separate from core engineering",
        ],
        "summary": (
            "The primary directive: resiliently add computing value -- code that is "
            "robust enough to withstand change, stress, and attack."
        ),
    },
    "2.3": {
        "title": "Security Mission: Reducing Material Impact",
        "when_to_use": [
            "defining the core mission of cybersecurity",
            "aligning security strategy with business objectives",
            "setting realistic security goals beyond breach elimination",
        ],
        "threats": [
            "pursuing the illusory goal of complete breach elimination",
            "security strategies misaligned with business objectives",
        ],
        "summary": (
            "The core mission is to reduce the probability of material impact of a "
            "cyber event. Security strategies must align with business objectives."
        ),
    },
    "2.4": {
        "title": "The Quality-Security Relationship",
        "ssem_pillar": "Maintainability",
        "ssem_attributes": ["Analyzability", "Modifiability", "Testability", "Observability"],
        "when_to_use": [
            "arguing that engineering quality investment is security investment",
            "explaining why security effort plateaus against low-quality code",
            "scoping what code quality can and cannot reach",
        ],
        "threats": [
            "security expertise hitting a hard ceiling set by unmaintainable code",
            "fixes that introduce new defects because the code resists change",
            "system behavior under attack that cannot be observed with enough fidelity",
        ],
        "summary": (
            "Security cannot exceed software quality; ISO/IEC 5055 codifies security "
            "as a structural quality characteristic measurable from source. Every "
            "downstream security activity is bounded by what the code makes possible."
        ),
    },
    "2.5": {
        "title": "Aligning Security with Development",
        "when_to_use": [
            "integrating security into development using engineering terminology",
            "empowering developers to address security confidently",
            "calibrating mindset expectations between security and development",
            "engaging AppSec early in requirements and design",
        ],
        "threats": [
            "imposing security-centric jargon that disrupts development",
            "expecting developers to adopt adversarial mindsets as primary defense",
            "AppSec engaging too late in the SDLC to add value",
        ],
        "summary": (
            "Security and development are complementary disciplines. True alignment "
            "uses established software engineering terms and engages AppSec early "
            "(Participation over Assessment)."
        ),
    },
    "2.6": {
        "title": "The Transparency Principle",
        "ssem_attributes": ["Observability", "Accountability"],
        "when_to_use": [
            "designing observable and auditable systems",
            "implementing logging and instrumentation strategies",
            "evaluating system transparency for security analysis",
            "connecting transparency to Maintainability and Trustworthiness",
        ],
        "threats": [
            "opaque systems that resist security analysis",
            "reactive security posture due to lack of observability",
            "insufficient audit trails for incident response",
        ],
        "summary": (
            "Transparency is a foundational engineering strategy: designing systems so "
            "internal state and behavior are observable and understandable to "
            "authorized parties."
        ),
    },
    "2.6.1": {
        "title": "Transparency and Maintainability",
        "ssem_pillar": "Maintainability",
        "ssem_attributes": ["Analyzability", "Observability"],
        "when_to_use": [
            "tracing data flow, state changes, and decision logic through logs",
            "connecting observability investment to diagnosis speed",
        ],
        "threats": [
            "deficiencies that cannot be diagnosed from external outputs",
            "change impact that cannot be assessed before shipping",
        ],
        "summary": (
            "A transparent system is easier to debug and understand. Structured logs "
            "and metrics let developers diagnose deficiencies and assess change "
            "effects with greater speed and accuracy."
        ),
    },
    "2.6.2": {
        "title": "Transparency and Trustworthiness",
        "ssem_pillar": "Trustworthiness",
        "ssem_attributes": ["Accountability", "Authenticity"],
        "when_to_use": [
            "establishing the audit trail that makes attribution possible",
            "logging authentication and authorization events for verification",
        ],
        "threats": [
            "actions that cannot be uniquely traced to an entity",
            "authentication events that leave no investigable record",
        ],
        "summary": (
            "Transparency is the mechanism that makes Accountability possible. "
            "Authenticity is reinforced when authentication and authorization events "
            "are transparently logged."
        ),
    },
    "2.6.3": {
        "title": "Transparency Tactics",
        "ssem_attributes": ["Observability", "Accountability", "Analyzability"],
        "when_to_use": [
            "choosing concrete tactics for structured logging and instrumentation",
            "specifying immutable audit trails for security-sensitive events",
            "logging boundary outcomes for validation and sanitization steps",
        ],
        "threats": [
            "unstructured logs that resist analysis, monitoring, and alerting",
            "audit trails missing the who, what, where, when, and why",
            "trust-boundary events that produce no signal",
        ],
        "summary": (
            "Practical tactics for engineering transparency: meaningful naming, "
            "version control history, structured log events, immutable audit trails, "
            "instrumented health metrics, and logging at trust boundaries."
        ),
    },
    "2.7": {
        "title": "The Principle of Least Astonishment",
        "ssem_attributes": ["Analyzability", "Modifiability"],
        "when_to_use": [
            "designing intuitive and predictable system behavior",
            "reviewing code for surprising or hidden side effects",
            "establishing consistent naming and error-handling conventions",
            "complementing transparency with predictable behavior",
        ],
        "threats": [
            "unexpected behavior that hides security-relevant decisions",
            "hidden side effects that bypass intended boundaries",
            "inconsistent interfaces that obscure trust assumptions",
        ],
        "summary": (
            "Systems should behave in ways that are intuitive and predictable. POLA "
            "supports Analyzability, Modifiability, and clearer security boundaries; "
            "it works in concert with the Transparency Principle."
        ),
    },
    # -----------------------------------------------------------------------
    # 3. The Securable Software Engineering Model (SSEM)
    # -----------------------------------------------------------------------
    "3.1": {
        "title": "Model Overview and Design Language",
        "ssem_pillar": "All",
        "ssem_attributes": [
            "Analyzability", "Modifiability", "Testability", "Observability",
            "Confidentiality", "Accountability", "Authenticity",
            "Availability", "Integrity", "Resilience",
        ],
        "when_to_use": [
            "introducing SSEM to a development team",
            "understanding the SSEM attribute taxonomy",
            "using SSEM as a design language for security discussions",
            "shifting the security question from binary to attribute-based",
        ],
        "threats": [
            "binary secure/insecure assessment without nuance",
            "security jargon that excludes developers",
            "find-and-fix monotony that does not scale",
        ],
        "summary": (
            "SSEM provides a design language using established software engineering "
            "terms. Ten attributes grouped into three pillars (Maintainability, "
            "Trustworthiness, Reliability)."
        ),
    },
    "3.2": {
        "title": "Core Securable Attributes",
        "ssem_pillar": "All",
        "ssem_attributes": [
            "Analyzability", "Modifiability", "Testability", "Observability",
            "Confidentiality", "Accountability", "Authenticity",
            "Availability", "Integrity", "Resilience",
        ],
        "when_to_use": [
            "introducing the SSEM attribute set as a whole",
            "framing the attributes as concrete engineering qualities",
        ],
        "threats": [
            "treating securable attributes as abstract goals rather than measurable qualities",
        ],
        "summary": (
            "The building blocks of securable software: tangible characteristics that "
            "contribute directly to a system's security and resilience."
        ),
    },
    "3.2.1": {
        "title": "Maintainability",
        "ssem_pillar": "Maintainability",
        "ssem_attributes": ["Analyzability", "Modifiability", "Testability", "Observability"],
        "when_to_use": [
            "reviewing code for maintainability attributes",
            "framing maintainability as a securable attribute",
        ],
        "threats": [
            "undetected vulnerabilities due to complex code",
            "slow vulnerability remediation",
            "introducing defects during security fixes",
        ],
        "summary": (
            "Maintainability encompasses Analyzability, Modifiability, Testability, "
            "and Observability -- the ability to evolve, correct, adapt, and observe "
            "software in operation."
        ),
    },
    "3.2.1.1": {
        "title": "Analyzability",
        "ssem_pillar": "Maintainability",
        "ssem_attributes": ["Analyzability"],
        "when_to_use": [
            "assessing analyzability of a codebase",
            "evaluating ability to locate causes of behavior in code",
            "establishing analyzability metrics for review",
        ],
        "threats": [
            "complex or duplicated code that obscures vulnerabilities",
            "outsized units that resist analysis",
            "imbalanced components that hide failure causes",
        ],
        "summary": (
            "The ability to locate the cause of a behavior within the code. Drives "
            "the speed and accuracy of vulnerability remediation."
        ),
    },
    "3.2.1.2": {
        "title": "Modifiability",
        "ssem_pillar": "Maintainability",
        "ssem_attributes": ["Modifiability"],
        "when_to_use": [
            "evaluating modifiability of a system",
            "assessing impact and coupling for safe change",
            "planning rapid response to newly discovered vulnerabilities",
        ],
        "threats": [
            "tightly coupled modules causing cascading change",
            "complex units that are hard to modify safely",
            "duplicated code producing inconsistent fixes",
        ],
        "summary": (
            "The ability to change code without breaking existing functionality or "
            "introducing new vulnerabilities. Enables rapid response to evolving threats."
        ),
    },
    "3.2.1.3": {
        "title": "Testability",
        "ssem_pillar": "Maintainability",
        "ssem_attributes": ["Testability"],
        "when_to_use": [
            "checking testability of code under review",
            "designing isolated, automatable test surfaces",
            "scaling security assurance via automated tests",
        ],
        "threats": [
            "untestable code masking regressions",
            "tightly coupled units that resist isolation",
            "test gaps in security-relevant paths",
        ],
        "summary": (
            "The ability to write a test for a piece of code without modifying the "
            "code under test. Enables continuous verification of security controls."
        ),
    },
    "3.2.1.4": {
        "title": "Observability",
        "ssem_pillar": "Maintainability",
        "ssem_attributes": ["Observability"],
        "when_to_use": [
            "designing logging, monitoring, and instrumentation",
            "evaluating runtime visibility of system behavior",
            "auditing whether observability is built into the code rather than bolted on",
            "designing UI feedback that surfaces meaningful state",
        ],
        "threats": [
            "opaque systems that depend on external tooling alone",
            "silent failures and exception swallowing",
            "log entries lacking sufficient context for incident analysis",
        ],
        "summary": (
            "The degree to which the internal state of a system can be inferred from "
            "its external outputs. Achieved through code-level instrumentation: "
            "structured logging, monitoring, instrumentation, and UI feedback."
        ),
    },
    "3.2.2": {
        "title": "Trustworthiness",
        "ssem_pillar": "Trustworthiness",
        "ssem_attributes": ["Confidentiality", "Accountability", "Authenticity"],
        "when_to_use": [
            "reviewing code for trustworthiness attributes",
            "assessing inherent qualities versus overlaid security controls",
        ],
        "threats": [
            "unauthorized data disclosure",
            "inability to trace actions to entities",
            "identity spoofing and non-repudiation failures",
        ],
        "summary": (
            "Trustworthiness encompasses Confidentiality, Accountability, and "
            "Authenticity -- the ability to meet stakeholder expectations in a "
            "verifiable way."
        ),
    },
    "3.2.2.1": {
        "title": "Confidentiality",
        "ssem_pillar": "Trustworthiness",
        "ssem_attributes": ["Confidentiality"],
        "when_to_use": [
            "assessing data protection at rest, in transit, and in use",
            "reviewing access controls and disclosure boundaries",
        ],
        "threats": [
            "unauthorized access to sensitive data",
            "leakage of information across trust boundaries",
        ],
        "summary": (
            "Property that information is not disclosed to unauthorized individuals, "
            "entities, or processes. Achieved through inherent protective qualities, "
            "not overlaid controls alone."
        ),
    },
    "3.2.2.2": {
        "title": "Accountability",
        "ssem_pillar": "Trustworthiness",
        "ssem_attributes": ["Accountability"],
        "when_to_use": [
            "evaluating audit trail design",
            "designing principal management and access attribution",
            "supporting incident response with traceable actions",
        ],
        "threats": [
            "actions that cannot be uniquely attributed to entities",
            "insufficient audit trails for incident response",
        ],
        "summary": (
            "Every action within a system is attributable to a specific, identified "
            "entity. Enables auditing and incident response."
        ),
    },
    "3.2.2.3": {
        "title": "Authenticity",
        "ssem_pillar": "Trustworthiness",
        "ssem_attributes": ["Authenticity"],
        "when_to_use": [
            "implementing or reviewing authentication mechanisms",
            "designing Defendable Authentication features",
            "applying signatures and certificates for identity verification",
        ],
        "threats": [
            "identity spoofing",
            "non-repudiation failures",
            "brittle authentication that cannot adapt to new attack patterns",
        ],
        "summary": (
            "The property that an entity is what it claims to be. Includes Defendable "
            "Authentication, digital signatures, and supporting non-repudiation."
        ),
    },
    "3.2.3": {
        "title": "Reliability",
        "ssem_pillar": "Reliability",
        "ssem_attributes": ["Availability", "Integrity", "Resilience"],
        "when_to_use": [
            "reviewing code for reliability attributes",
            "assessing predictable operation under adverse conditions",
        ],
        "threats": [
            "denial of service attacks",
            "unauthorized data modification or corruption",
            "system failures and inability to recover",
        ],
        "summary": (
            "Reliability encompasses Availability, Integrity, and Resilience -- "
            "consistent and predictable operation under adverse conditions."
        ),
    },
    "3.2.3.1": {
        "title": "Availability",
        "ssem_pillar": "Reliability",
        "ssem_attributes": ["Availability"],
        "when_to_use": [
            "assessing uptime and recovery design",
            "designing resistance to DDoS and similar attacks",
        ],
        "threats": [
            "denial of service attacks",
            "extended downtime from unmonitored failure modes",
        ],
        "summary": (
            "Property of being accessible and usable on demand by authorized "
            "entities, including during adverse circumstances."
        ),
    },
    "3.2.3.2": {
        "title": "Integrity",
        "ssem_pillar": "Reliability",
        "ssem_attributes": ["Integrity"],
        "when_to_use": [
            "evaluating data and system integrity",
            "applying derived integrity to business-critical state",
            "implementing cryptographic hashing, checksums, and access controls",
        ],
        "threats": [
            "unauthorized modification of code, configuration, or data",
            "business logic manipulation through client-supplied state",
        ],
        "summary": (
            "Property of accuracy and completeness. Applies at both system and data "
            "levels; supported by the Isolated Integrity Principle (Section 4.4.1.2)."
        ),
    },
    "3.2.3.3": {
        "title": "Resilience",
        "ssem_pillar": "Reliability",
        "ssem_attributes": ["Resilience"],
        "when_to_use": [
            "designing for fault tolerance and graceful degradation",
            "reviewing recovery and error-handling paths",
            "applying defensive coding (Section 4.4)",
        ],
        "threats": [
            "cascading failures from unhandled component faults",
            "non-graceful failure that exposes system internals",
        ],
        "summary": (
            "The ability of a system to continue operating during and after failure, "
            "and to recover. Includes fault tolerance, defensive coding, and strong "
            "trust boundaries."
        ),
    },
    # -----------------------------------------------------------------------
    # 4. Practical Guidance for Securable Software Development
    # -----------------------------------------------------------------------
    "4.1": {
        "title": "Establishing Clear Expectations",
        "when_to_use": [
            "setting security expectations for development teams",
            "integrating security into requirements gathering",
            "improving proactive communication between AppSec and Dev",
        ],
        "threats": [
            "unclear security expectations leading to missing controls",
            "security imposed as afterthought rather than requirement",
            "implementation deficient by design due to incomplete requirements",
        ],
        "summary": (
            "Clear expectations through proactive communication and integrating "
            "security into requirements (features, threat scenarios, acceptance criteria)."
        ),
    },
    "4.1.1": {
        "title": "Proactive Communication",
        "when_to_use": [
            "rolling out new security testing initiatives to developers",
            "establishing regular AppSec-Development synchronization",
        ],
        "threats": [
            "AppSec initiatives launched without dev awareness or buy-in",
            "loss of momentum after initial security rollouts",
        ],
        "summary": (
            "Inform development teams about new initiatives, demonstrate tools, and "
            "maintain regular synchronization to sustain partnership."
        ),
    },
    "4.1.2": {
        "title": "Integrating Security into Requirements",
        "when_to_use": [
            "authoring security features, threat scenarios, and acceptance criteria",
            "moving security from post-development review to integral requirement",
            "establishing measurable security outcomes via implementation completeness",
        ],
        "threats": [
            "security gaps rooted in requirements that never specified them",
            "QA unable to verify security expectations because none were defined",
        ],
        "summary": (
            "Active AppSec participation in requirements gathering. Key deliverables: "
            "Security Features, Threat Scenarios, and Security Acceptance Criteria."
        ),
    },
    "4.2": {
        "title": "Threat Modeling",
        "when_to_use": [
            "performing threat modeling activities",
            "distinguishing formal threat modeling from threat awareness",
            "selecting a methodology (STRIDE, PASTA, LINDDUN)",
        ],
        "threats": [
            "conflating informal threat awareness with formal threat modeling",
            "design-level threats missed because only code-level review occurred",
        ],
        "summary": (
            "Two distinct activities: formal Threat Modeling at the system/feature "
            "level, and continuous lightweight Threat Awareness at the code level."
        ),
    },
    "4.2.1": {
        "title": "Code-Level Threat Awareness",
        "when_to_use": [
            "applying the 'What can go wrong?' question during merge reviews",
            "incorporating static analysis findings into threat awareness",
            "using pair programming to build threat-awareness judgment",
        ],
        "threats": [
            "code-level findings that never escalate into the formal threat model",
            "missed design-level concerns in scoped reviews",
        ],
        "summary": (
            "Lightweight, continuous practice of asking 'What can go wrong?' at the "
            "code level. Findings that reveal design-level concerns must escalate "
            "into the formal threat model."
        ),
    },
    "4.2.2": {
        "title": "Threat Modeling Solution Framework",
        "when_to_use": [
            "answering 'What are we going to do about it?' with SSEM",
            "deriving security requirements from unaddressable threats",
            "mapping data flows to identify trust boundaries",
        ],
        "threats": [
            "default reach for security controls without considering inherent attributes",
            "threats addressed by localized fixes rather than design changes",
        ],
        "summary": (
            "Use SSEM (especially Trustworthiness and Reliability) to find inherent "
            "architectural solutions; gaps that cannot be addressed inherently become "
            "explicit security requirements."
        ),
    },
    "4.3": {
        "title": "The Boundary Control Principle",
        "ssem_attributes": ["Integrity", "Resilience", "Confidentiality"],
        "when_to_use": [
            "designing trust boundary handling",
            "balancing internal flexibility with control at boundaries",
            "applying canonical input handling at trust boundaries",
        ],
        "threats": [
            "uncontrolled flexibility at trust boundaries enabling injection attacks",
            "treating flexibility itself as the threat rather than its exposure",
        ],
        "summary": (
            "Flexibility within the interior is an engineering asset; control at "
            "every trust boundary is a security requirement. Harden the shell, keep "
            "the interior flexible. (Formerly called 'The Flexibility Principle'.)"
        ),
    },
    "4.4": {
        "title": "Resilient Coding",
        "ssem_pillar": "Reliability",
        "ssem_attributes": ["Resilience", "Integrity", "Observability"],
        "when_to_use": [
            "implementing defensive coding practices",
            "reviewing input handling, error handling, and resource management",
            "applying least privilege at the code level",
            "designing for graceful and secure failure",
        ],
        "threats": [
            "injection attacks from unvalidated input",
            "resource leaks introducing availability or memory risks",
            "error paths leaking internal state to untrusted parties",
            "code retaining elevated privileges longer than required",
        ],
        "summary": (
            "Defensive coding practices that produce predictable, recoverable "
            "behavior: strong typing, input validation, output encoding, safe "
            "resource management, graceful and secure failure, and least privilege "
            "at the code level."
        ),
    },
    "4.4.1": {
        "title": "Canonical Input Handling",
        "ssem_attributes": ["Integrity", "Resilience"],
        "when_to_use": [
            "designing input validation strategies at trust boundaries",
            "applying canonicalization, validation, and sanitization",
            "passing contextualized objects after validation",
        ],
        "threats": [
            "malformed or malicious input propagating into core logic",
            "sanitization gaps that miss context-specific encodings",
        ],
        "summary": (
            "Apply minimum acceptable range at the point of input through "
            "canonicalization/normalization, validation, and sanitization."
        ),
    },
    "4.4.1.1": {
        "title": "The Canonical Parsing Principle",
        "ssem_attributes": ["Integrity", "Resilience", "Observability", "Analyzability"],
        "when_to_use": [
            "parsing external input into a canonical typed structure at the boundary",
            "defining an explicit input schema per operation instead of a generic envelope",
            "logging and rejecting schema deviations in sensitive contexts",
            "detecting reconnaissance and probing behavior",
        ],
        "threats": [
            "loosely typed data revalidated repeatedly instead of parsed once",
            "blanket processing of request envelopes enabling injection",
            "silent acceptance of unexpected fields enabling reconnaissance",
            "manipulation of derived values via extra fields",
        ],
        "summary": (
            "Parse, don't validate: perform one strict parse at the trust boundary "
            "into a canonical internal type and fail closed if it does not succeed. "
            "The resulting structure is proof that required invariants hold."
        ),
    },
    "4.4.1.2": {
        "title": "The Isolated Integrity Principle",
        "ssem_attributes": ["Integrity", "Authenticity"],
        "when_to_use": [
            "deriving prices, totals, and other authoritative values server-side",
            "managing user permissions and object state from trusted sources",
            "validating JWT signature algorithms server-side",
            "asking whether an untrusted caller could set or bias a critical value",
        ],
        "threats": [
            "business logic manipulation through client-supplied authoritative values",
            "JWT algorithm-confusion attacks",
            "client-supplied permission elevation",
        ],
        "summary": (
            "Isolation of authority: integrity-critical facts must be controlled by "
            "server-side logic and data sources a client cannot set, override, or "
            "indirectly bias. The client expresses intent; the server enforces facts."
        ),
    },
    "4.5": {
        "title": "Dependency Management",
        "ssem_attributes": [
            "Analyzability", "Modifiability", "Testability",
            "Authenticity", "Integrity", "Resilience",
        ],
        "when_to_use": [
            "evaluating third-party library adoption",
            "applying SSEM to dependency selection and management",
            "going beyond CVE scanning to assess transitive risk",
        ],
        "threats": [
            "insecure dependencies introducing vulnerabilities",
            "supply chain attacks through tampered packages",
            "unnecessary dependencies expanding attack surface",
        ],
        "summary": (
            "Evaluate dependencies against SSEM attributes before introduction. "
            "Minimize dependencies, update regularly, go beyond CVE scanning."
        ),
    },
    "4.6": {
        "title": "Dependency Stewardship",
        "ssem_attributes": [
            "Analyzability", "Modifiability", "Testability",
            "Authenticity", "Integrity", "Resilience",
        ],
        "when_to_use": [
            "treating ongoing dependency relationships as a securable attribute",
            "monitoring dependency health and maintainer activity over time",
            "raising stewardship in sprint planning, architecture, and merge reviews",
        ],
        "threats": [
            "dependencies that decay after initial evaluation",
            "abandoned or compromised maintainer communities",
            "tightly coupled dependencies that resist replacement",
        ],
        "summary": (
            "The ongoing application of SSEM attributes to dependency selection, "
            "integration, monitoring, and lifecycle management. Stewardship asks: "
            "would this dependency be responsible, maintainable, and trustworthy "
            "now and over time?"
        ),
    },
    # -----------------------------------------------------------------------
    # 5. Integrating Security into Development Processes
    # -----------------------------------------------------------------------
    "5.1": {
        "title": "Natively Extending Development Processes",
        "when_to_use": [
            "integrating security into existing dev workflows",
            "repositioning security as a partner rather than gatekeeper",
            "extending architecture, checklists, and usability with security",
        ],
        "threats": [
            "imposing external security gates that disrupt development",
            "adversarial relationship between security and development",
        ],
        "summary": (
            "Integrate security into existing workflows rather than imposing "
            "separate gates. Security as partner in design, not external assessor."
        ),
    },
    "5.2": {
        "title": "The Role of Merge Reviews",
        "when_to_use": [
            "establishing security-focused code review practices",
            "scaling securable code review through pull/merge requests",
            "treating reviews as guardrails rather than gates",
        ],
        "threats": [
            "security vulnerabilities missed without structured review",
            "review processes that become friction rather than guidance",
        ],
        "summary": (
            "Merge reviews are an effective scaling point for securable review and "
            "knowledge transfer. SSEM attributes provide a shared review basis. "
            "Sections 5.2.1-5.2.5 define the mechanism that makes the guardrail "
            "concrete."
        ),
    },
    "5.2.1": {
        "title": "The Securability Report",
        "when_to_use": [
            "defining the artifact a securability review produces on every merge",
            "combining automated scanning with reviewer assessment in SSEM vocabulary",
            "scaling securable review where whole-application review cannot",
        ],
        "threats": [
            "automation output presented without architectural context",
            "review attention spread evenly instead of directed by risk",
        ],
        "summary": (
            "Every merge produces an informational report: automated analysis scoped "
            "to the changeset, plus reviewer assessment expressed in SSEM vocabulary. "
            "Generated unconditionally; blocks nothing by default."
        ),
    },
    "5.2.2": {
        "title": "The Advisory Default",
        "when_to_use": [
            "justifying why the securability report blocks nothing by default",
            "using merge review as a teaching instrument for SSEM reasoning",
        ],
        "threats": [
            "review friction that turns securability into a compliance ritual",
            "one-off corrections that never become transferable patterns",
        ],
        "summary": (
            "The report makes securability consequences visible when a change is "
            "cheapest to discuss. Read this way it is a teaching instrument, turning "
            "review comments into transferable patterns."
        ),
    },
    "5.2.3": {
        "title": "Gating as a Policy Decision",
        "ssem_attributes": ["Accountability"],
        "when_to_use": [
            "elevating designated finding classes to blocking status",
            "designing an override path with recorded authority",
        ],
        "threats": [
            "gating without an override path stalling delivery",
            "acceptance decisions made without an attributable record",
        ],
        "summary": (
            "Gating is a policy decision, not a framework default. Wherever gating is "
            "enabled an override path must exist; exercising it is the mechanism "
            "completing, with the business retaining authority to accept risk."
        ),
    },
    "5.2.4": {
        "title": "The Audit Trail",
        "ssem_attributes": ["Accountability"],
        "when_to_use": [
            "producing compliance evidence as a by-product of ordinary work",
            "mapping merge-review records onto CRA and NIST SP 800-218 obligations",
        ],
        "threats": [
            "evidence reconstructed after the fact rather than captured as it happens",
            "acceptance decisions that cannot be attributed to a named authority",
        ],
        "summary": (
            "The mechanism produces a structured, timestamped, attributable audit "
            "trail of findings, gating decisions, and overrides. This is what "
            "proof-based compliance consumes."
        ),
    },
    "5.2.5": {
        "title": "Posture over Pass Rates",
        "when_to_use": [
            "measuring security posture over time rather than per-merge pass rates",
            "reading recurring overrides as an upstream signal",
        ],
        "threats": [
            "enforcing harder at the merge instead of fixing the requirements gap",
            "pass rate optimization that hides a systemic weakness",
        ],
        "summary": (
            "What the organization manages is posture over time, not the pass rate of "
            "individual merges. A recurring override on the same finding class points "
            "upstream to a requirements or securability gap."
        ),
    },
    "5.3": {
        "title": "Early Integration: Planning and Requirements",
        "when_to_use": [
            "integrating security into requirements gathering",
            "defining security acceptance criteria for features",
            "shifting security to a design-phase concern",
        ],
        "threats": [
            "security treated as post-development afterthought",
            "vulnerabilities discovered late at significantly higher remediation cost",
        ],
        "summary": (
            "Set security expectations at planning and requirements. Active AppSec "
            "participation in requirements (Section 4.1.2) is the primary mechanism."
        ),
    },
    # -----------------------------------------------------------------------
    # 6. Common AppSec Anti-Patterns
    # -----------------------------------------------------------------------
    "6.1": {
        "title": "Security Controls in the Code Creation Process",
        "when_to_use": [
            "distinguishing catalog controls, requirements, features, and evidence",
            "translating a control catalog into implementable requirements",
            "diagnosing why a control-shaped demand cannot be built as written",
        ],
        "threats": [
            "catalog controls handed to development as if they were specifications",
            "controls assumed satisfied because they are documented somewhere",
            "unallocated controls that each team assumes the other owns",
        ],
        "summary": (
            "Four artifacts collapse into the word 'control': catalog control, "
            "security requirement, security feature, and verification evidence. "
            "Skipping the translation between them produces two predictable failures."
        ),
    },
    "6.1.1": {
        "title": "The Control-as-Requirement Fallacy",
        "when_to_use": [
            "recognizing catalog items presented as programmer specifications",
            "translating an implementation-agnostic control into acceptance criteria",
        ],
        "threats": [
            "developers expected to infer an implementation from a system-scoped control",
            "friction landing on development instead of on the missing process",
        ],
        "summary": (
            "Treating a catalog item as a specification the programmer should already "
            "know to build. A control like AC-3 is not verifiable against a codebase "
            "until it is translated into observable behavior with criteria."
        ),
    },
    "6.1.2": {
        "title": "The Control-as-Protection Fallacy",
        "when_to_use": [
            "identifying residual code obligations behind externally-satisfied controls",
            "allocating control ownership across platform, network, process, and code",
        ],
        "threats": [
            "environment-provided protection assumed to be a property of the software",
            "residual obligations unspecified because 'the control is handled'",
        ],
        "summary": (
            "Reading the documented existence of a control as a property of the "
            "software. Correctly-external controls still leave residual obligations "
            "inside the code, such as failing closed when upstream protection is absent."
        ),
    },
    "6.1.3": {
        "title": "The Requirements Process as the Corrective",
        "when_to_use": [
            "allocating, specifying, and verifying the code's share of a control",
            "using ASVS as a ready-made requirements library",
            "treating the catalog as a floor rather than a ceiling",
        ],
        "threats": [
            "point-in-time attestation mistaken for a durable property",
            "control-shaped demands arriving without acceptance criteria",
        ],
        "summary": (
            "Allocation, specification, and adequacy supply what the catalog omits. "
            "A control describes a protection; a requirement specifies behavior; a "
            "feature delivers it; evidence proves it."
        ),
    },
    "6.2": {
        "title": "The Shoveling Left Phenomenon",
        "when_to_use": [
            "identifying ineffective AppSec practices",
            "applying the Actionable Security Intelligence Principle",
            "evaluating how security findings reach developers",
        ],
        "threats": [
            "raw vulnerability dumps overwhelming developers",
            "exploit-first training that fails to build engineering skills",
            "developer disengagement from AppSec",
        ],
        "summary": (
            "Shoveling Left: supplying impractical information to developers. The "
            "corrective discipline is the Actionable Security Intelligence Principle."
        ),
    },
    "6.2.1": {
        "title": "Ineffective Vulnerability Reporting",
        "when_to_use": [
            "improving how scanner findings reach development",
            "validating, prioritizing, and root-cause-grouping findings",
        ],
        "threats": [
            "raw scanner output routed directly to backlog",
            "whack-a-mole patterns from unaddressed root causes",
        ],
        "summary": (
            "Avoid routing raw scanner output to development. Validate true "
            "positives, identify root causes, prioritize impact, and verify fixes."
        ),
    },
    "6.2.2": {
        "title": "Pitfalls of Exploit-First Training",
        "when_to_use": [
            "evaluating developer security training effectiveness",
            "designing training grounded in engineering principles, not exploitation",
        ],
        "threats": [
            "training that emphasizes exploitation over engineering",
            "false sense of security from superficial exploit knowledge",
        ],
        "summary": (
            "Training centered on exploitation does not equip developers with the "
            "engineering principles needed to build inherently securable systems."
        ),
    },
    "6.3": {
        "title": "Strategic Use of Security Output",
        "when_to_use": [
            "establishing processes for sharing scanning and testing results",
            "avoiding disruption of developer workflows",
            "translating raw findings into actionable intelligence",
        ],
        "threats": [
            "fix requests bypassing established workflows",
            "treating scanner output as finished intelligence rather than input",
        ],
        "summary": (
            "Scanning and testing output must be converted into engineering-grounded "
            "direction tied to requirements and acceptance criteria, not handed to "
            "developers as finished intelligence."
        ),
    },
    # -----------------------------------------------------------------------
    # 7. Roles and Responsibilities
    # -----------------------------------------------------------------------
    "7.1": {
        "title": "The Role of the Security Team",
        "when_to_use": [
            "defining the role of AppSec in development organizations",
            "framing security metrics as partnership measures",
            "investing security effort in design and requirements",
        ],
        "threats": [
            "security metrics misattributed as developer compliance measures",
            "security team policing line-level fixes instead of partnering",
        ],
        "summary": (
            "Security metrics measure partnership effectiveness, not developer "
            "adherence. The security team's effectiveness is limited by software "
            "quality."
        ),
    },
    "7.1.1": {
        "title": "The Strategic Case for the Shift",
        "when_to_use": [
            "justifying the move from end-of-cycle assessment to upstream participation",
            "locating the leverage point for security effort in the lifecycle",
        ],
        "threats": [
            "security arriving at the end with a finding list",
            "leverage spent on testing rather than on requirements and design",
        ],
        "summary": (
            "The leverage point is earlier and further upstream than testing. "
            "Requirements, design, and architecture are where security expectations "
            "become structural."
        ),
    },
    "7.1.2": {
        "title": "Capacity Relief Through Agentic AppSec",
        "when_to_use": [
            "adopting agentic tooling to free reviewer capacity",
            "tying freed capacity to specific upstream engagements",
        ],
        "threats": [
            "agentic tooling producing higher-volume Shoveling Left",
            "capacity freed but never reinvested upstream",
        ],
        "summary": (
            "Agentic tooling relieves the mechanical portion of the reviewer role. "
            "The capacity it frees must be tied to specific upstream engagements or "
            "it just increases finding volume."
        ),
    },
    "7.1.3": {
        "title": "Transition, Not Switchover",
        "when_to_use": [
            "sequencing the security team's role change over time",
            "sustaining assurance work while participation is grown into",
        ],
        "threats": [
            "assurance capability abandoned before participation is established",
        ],
        "summary": (
            "The role shift is a transition, not a switchover. Assurance work "
            "continues while participation is grown into."
        ),
    },
    "7.1.4": {
        "title": "Business-Leadership Alignment Is a Precondition",
        "when_to_use": [
            "assessing whether the security role shift is viable in an organization",
            "naming leadership backing as an adoption prerequisite",
        ],
        "threats": [
            "role shift attempted without leadership backing",
            "adoption failure misdiagnosed as framework failure",
        ],
        "summary": (
            "The shift depends on business-leadership alignment as a precondition, "
            "not as a later ratification."
        ),
    },
    "7.1.5": {
        "title": "Staffing Implications",
        "when_to_use": [
            "planning the skill mix a participating security team requires",
        ],
        "threats": [
            "staffing profile unchanged while the role's demands change",
        ],
        "summary": (
            "Staffing implications of moving security effort upstream into "
            "requirements and design participation."
        ),
    },
    "7.2": {
        "title": "Senior Software Engineers",
        "when_to_use": [
            "defining expectations for senior engineers in FIASSE adoption",
            "establishing senior engineers as primary technical partners for security",
            "scrutinizing AI-generated code for SSEM attribute alignment",
        ],
        "threats": [
            "senior engineers not engaged in security considerations",
            "AI-generated code accepted without judgment about trust boundaries",
        ],
        "summary": (
            "Senior engineers drive security requirements, lead SSEM-based merge "
            "reviews, maintain prompt engineering standards for AI-assisted "
            "generation, and mentor peers."
        ),
    },
    "7.3": {
        "title": "Developing Software Engineers",
        "when_to_use": [
            "mentoring developing engineers in securable practices",
            "establishing learning paths grounded in engineering fundamentals",
            "building SSEM mental models in less experienced team members",
        ],
        "threats": [
            "developing engineers introducing vulnerabilities from inexperience",
            "AI-generated code accepted without critical review",
        ],
        "summary": (
            "Developing engineers benefit from SSEM mental models. Focus on "
            "engineering fundamentals, defensive coding, trust boundaries, and "
            "scrutinizing AI-generated code."
        ),
    },
    "7.4": {
        "title": "Product Owners and Managers",
        "when_to_use": [
            "engaging product owners in security planning",
            "allocating time for security activities and dependency maintenance",
            "evaluating scope cuts for securability impact",
        ],
        "threats": [
            "scope cuts that silently degrade securable attributes",
            "vendor selection without securability evaluation",
            "security activities deprioritized in product planning",
        ],
        "summary": (
            "FIASSE-literate Product Owners assess backlog items for securability "
            "implications, validate security acceptance criteria, and recognize "
            "when scope cuts erode securable attributes."
        ),
    },
    # -----------------------------------------------------------------------
    # 8. Organizational Adoption of FIASSE
    # -----------------------------------------------------------------------
    "8": {
        "title": "Organizational Adoption of FIASSE",
        "when_to_use": [
            "planning organizational adoption of FIASSE",
            "assessing readiness and identifying influencers",
            "integrating SSEM terminology into standards and training",
        ],
        "threats": [
            "FIASSE treated as a separate security initiative",
            "failed adoption from lack of stakeholder buy-in",
        ],
        "summary": (
            "Seven-step adoption path: assess practices, integrate SSEM terminology, "
            "identify influencers, educate teams, adopt agentic tooling as capacity "
            "relief, foster collaboration, and monitor continuously."
        ),
    },
    "8.1": {
        "title": "Degraded-Mode Adoption",
        "when_to_use": [
            "adopting FIASSE where a prerequisite is thin or absent",
            "naming gaps instead of claiming full adoption",
        ],
        "threats": [
            "claiming full adoption while operating without the prerequisites",
            "adoption abandoned because a prerequisite is missing",
        ],
        "summary": (
            "FIASSE is adoptable around a gap (sparse requirements, thin senior "
            "bench, weak review culture) when the gap is named. This is a legitimate "
            "posture; claiming full adoption without the prerequisites is not."
        ),
    },
    "8.1.1": {
        "title": "Compensate with Agentic Assistance",
        "when_to_use": [
            "expanding throughput where senior-engineer hours are scarce",
        ],
        "threats": [
            "agentic tooling mistaken for the judgment a senior bench provides",
        ],
        "summary": (
            "AI-assisted tooling can expand throughput that would otherwise consume "
            "scarce senior-engineer hours, without replacing the judgment the bench "
            "exists to provide."
        ),
    },
    "8.1.2": {
        "title": "Invest in the Prerequisite First",
        "when_to_use": [
            "deciding whether to build the prerequisite before adopting",
        ],
        "threats": [
            "adoption layered on a foundation that cannot support it",
        ],
        "summary": (
            "Where the gap is large, invest in requirements-process work, engineering "
            "culture, or senior hiring before or alongside adoption."
        ),
    },
    "8.1.3": {
        "title": "Adopt Partially with Named Gaps",
        "when_to_use": [
            "starting with the parts the prerequisites support",
            "recording what is deferred so partial adoption is not overstated",
        ],
        "threats": [
            "partial adoption mistaken for full adoption",
        ],
        "summary": (
            "Start with what the prerequisites support and name what is deferred, so "
            "partial adoption is not mistaken for full adoption."
        ),
    },
    "8.2": {
        "title": "Indicators of Adoption Effectiveness",
        "when_to_use": [
            "measuring whether FIASSE adoption is working",
            "separating leading from lagging adoption signals",
        ],
        "threats": [
            "adoption judged on activity rather than on effect",
        ],
        "summary": (
            "Leading indicators appear within one to two quarters; lagging indicators "
            "within one to two years. The pattern between them diagnoses adoption "
            "failure versus framework fit."
        ),
    },
    "8.2.1": {
        "title": "Leading Indicators",
        "when_to_use": [
            "checking for adoption movement within one to two quarters",
        ],
        "threats": [
            "no visible change in how requirements and reviews are conducted",
        ],
        "summary": (
            "Security acceptance criteria appear on user stories as a matter of "
            "course; threat scenarios are recorded during requirements; merge reviews "
            "reference SSEM attributes as design language."
        ),
    },
    "8.2.2": {
        "title": "Lagging Indicators",
        "when_to_use": [
            "checking for adoption effect within one to two years",
        ],
        "threats": [
            "findings churn and regressing fixes persisting after adoption",
        ],
        "summary": (
            "Findings churn declines, fixes stay fixed, turnaround shortens, and the "
            "vulnerability class distribution shifts toward classes outside what "
            "upstream requirements can reach."
        ),
    },
    "8.2.3": {
        "title": "Distinguishing Framework Failure from Adoption Failure",
        "when_to_use": [
            "diagnosing why indicators are not moving",
            "deciding between a longer runway and an honest reassessment",
        ],
        "threats": [
            "adoption failure misread as framework failure, or the reverse",
        ],
        "summary": (
            "Leading indicators that do not move point to adoption failure: a missed "
            "prerequisite or missing leadership backing. Leading indicators moving "
            "without lagging ones warrants an honest reassessment of fit."
        ),
    },
    # -----------------------------------------------------------------------
    # Appendix A. Measuring SSEM Attributes
    # -----------------------------------------------------------------------
    "A.1": {
        "title": "Measuring Maintainability",
        "ssem_pillar": "Maintainability",
        "ssem_attributes": ["Analyzability", "Modifiability", "Testability", "Observability"],
        "when_to_use": [
            "establishing metrics for maintainability attributes",
            "defining measurement criteria for securability reviews",
        ],
        "threats": [
            "unmeasured code quality degrading over time",
            "inability to track improvement in securable attributes",
        ],
        "summary": (
            "Quantitative and qualitative measurement approaches for Analyzability, "
            "Modifiability, Testability, and Observability."
        ),
    },
    "A.1.1": {
        "title": "Measuring Analyzability",
        "ssem_pillar": "Maintainability",
        "ssem_attributes": ["Analyzability"],
        "when_to_use": [
            "tracking volume, duplication, unit size, and complexity",
            "running developer surveys and time-to-understand assessments",
        ],
        "threats": ["analyzability decay obscuring vulnerabilities"],
        "summary": "Quantitative and qualitative measures for Analyzability.",
    },
    "A.1.2": {
        "title": "Measuring Modifiability",
        "ssem_pillar": "Maintainability",
        "ssem_attributes": ["Modifiability"],
        "when_to_use": [
            "tracking module coupling, change impact size, and regression rate",
            "assessing time-to-implement and ease-of-change qualitatively",
        ],
        "threats": ["high coupling causing cascading change"],
        "summary": "Quantitative and qualitative measures for Modifiability.",
    },
    "A.1.3": {
        "title": "Measuring Testability",
        "ssem_pillar": "Maintainability",
        "ssem_attributes": ["Testability"],
        "when_to_use": [
            "tracking code coverage, unit test density, and mocking complexity",
            "evaluating ease of writing tests and execution time",
        ],
        "threats": ["test gaps in security-relevant paths"],
        "summary": "Quantitative and qualitative measures for Testability.",
    },
    "A.1.4": {
        "title": "Measuring Observability",
        "ssem_pillar": "Maintainability",
        "ssem_attributes": ["Observability"],
        "when_to_use": [
            "tracking log coverage, instrumentation coverage, alert SNR, and MTTD",
            "auditing structured-logging quality and code-level instrumentation",
            "identifying silent failure paths",
        ],
        "threats": [
            "silent failures and exception swallowing",
            "instrumentation gaps creating opaque code paths",
        ],
        "summary": (
            "Quantitative and qualitative measures for Observability, including "
            "structured logging review, instrumentation audits, and failure-path "
            "observability."
        ),
    },
    "A.2": {
        "title": "Measuring Trustworthiness",
        "ssem_pillar": "Trustworthiness",
        "ssem_attributes": ["Confidentiality", "Accountability", "Authenticity"],
        "when_to_use": [
            "establishing metrics for trustworthiness attributes",
            "auditing data protection, access controls, and authentication coverage",
        ],
        "threats": [
            "data leaks from insufficient confidentiality controls",
            "untraceable actions due to poor accountability",
        ],
        "summary": (
            "Quantitative and qualitative measurement approaches for "
            "Confidentiality, Accountability, and Authenticity."
        ),
    },
    "A.2.1": {
        "title": "Measuring Confidentiality",
        "ssem_pillar": "Trustworthiness",
        "ssem_attributes": ["Confidentiality"],
        "when_to_use": [
            "tracking identified data leaks and access control violations",
            "reviewing data classification and least-privilege adherence",
        ],
        "threats": ["uncontrolled data disclosure"],
        "summary": "Quantitative and qualitative measures for Confidentiality.",
    },
    "A.2.2": {
        "title": "Measuring Accountability",
        "ssem_pillar": "Trustworthiness",
        "ssem_attributes": ["Accountability"],
        "when_to_use": [
            "tracking audit log coverage and traceability success rate",
            "assessing non-repudiation strength",
        ],
        "threats": ["actions that cannot be uniquely attributed"],
        "summary": "Quantitative and qualitative measures for Accountability.",
    },
    "A.2.3": {
        "title": "Measuring Authenticity",
        "ssem_pillar": "Trustworthiness",
        "ssem_attributes": ["Authenticity"],
        "when_to_use": [
            "tracking authentication failures and mechanism coverage",
            "assessing adaptability of authentication mechanisms",
        ],
        "threats": ["brittle authentication that cannot adapt"],
        "summary": "Quantitative and qualitative measures for Authenticity.",
    },
    "A.3": {
        "title": "Measuring Reliability",
        "ssem_pillar": "Reliability",
        "ssem_attributes": ["Availability", "Integrity", "Resilience"],
        "when_to_use": [
            "establishing metrics for reliability attributes",
            "measuring uptime, recovery, and resilience under stress",
        ],
        "threats": [
            "prolonged downtime from unmonitored availability",
            "undetected data corruption",
        ],
        "summary": (
            "Quantitative and qualitative measurement approaches for Availability, "
            "Integrity, and Resilience."
        ),
    },
    "A.3.1": {
        "title": "Measuring Availability",
        "ssem_pillar": "Reliability",
        "ssem_attributes": ["Availability"],
        "when_to_use": [
            "tracking uptime percentage, MTBF, MTTR",
            "reviewing redundancy and disaster recovery test results",
        ],
        "threats": ["service disruption and slow recovery"],
        "summary": "Quantitative and qualitative measures for Availability.",
    },
    "A.3.2": {
        "title": "Measuring Integrity",
        "ssem_pillar": "Reliability",
        "ssem_attributes": ["Integrity"],
        "when_to_use": [
            "tracking corruption incidents and checksum/hash validation rates",
            "reviewing input validation and file integrity monitoring",
        ],
        "threats": ["unauthorized data modification"],
        "summary": "Quantitative and qualitative measures for Integrity.",
    },
    "A.3.3": {
        "title": "Measuring Resilience",
        "ssem_pillar": "Reliability",
        "ssem_attributes": ["Resilience"],
        "when_to_use": [
            "tracking RTO adherence and performance under stress",
            "reviewing defensive coding practices",
        ],
        "threats": ["cascading failures and slow recovery"],
        "summary": "Quantitative and qualitative measures for Resilience.",
    },
    "A.4": {
        "title": "Scoring and Enhancement Suggestions",
        "ssem_pillar": "All",
        "ssem_attributes": [
            "Analyzability", "Modifiability", "Testability", "Observability",
            "Confidentiality", "Accountability", "Authenticity",
            "Availability", "Integrity", "Resilience",
        ],
        "when_to_use": [
            "combining SSEM indicators into a composite score",
            "pairing a score with attribute-specific enhancement suggestions",
            "reporting deltas against a prior scan so change is visible",
            "deciding when a scored finding needs reviewer confirmation",
        ],
        "threats": [
            "a composite score mistaken for a statement of assurance or compliance",
            "false precision from a single number standing in for posture",
            "teams optimizing for the score at the expense of the architecture",
        ],
        "summary": (
            "A composite score is a directional management aid, not a statement of "
            "assurance. Useful for comparing a system against itself over time and "
            "for surfacing the weakest attributes first. Pair it with suggestions "
            "that are attribute-specific, actionable, evidence-based, comparable over "
            "time, context-aware, and reviewed when material. The most useful output "
            "has three parts: the score, the rationale, and prioritized changes."
        ),
    },
}

# ---------------------------------------------------------------------------
# Section-ID mapping to framework heading patterns
# ---------------------------------------------------------------------------
# The FIASSE framework uses numbered headings (## 1. Introduction, ### 1.1., etc.).
# In v1.1, headings range from level 2 (chapters) down to level 5
# (sub-sub-attributes like ##### 4.4.1.1).

# Ordered list of section IDs to extract. Order is significant: each section
# extends until the next sibling listed here, or until a chapter heading
# (whichever comes first).
TARGET_SECTIONS: list[str] = [
    # 1. Introduction
    "1.1", "1.2",
    # 2. Foundational Principles
    "2.1", "2.2", "2.3", "2.4", "2.5",
    "2.6", "2.6.1", "2.6.2", "2.6.3",
    "2.7",
    # 3. SSEM
    "3.1", "3.2",
    "3.2.1", "3.2.1.1", "3.2.1.2", "3.2.1.3", "3.2.1.4",
    "3.2.2", "3.2.2.1", "3.2.2.2", "3.2.2.3",
    "3.2.3", "3.2.3.1", "3.2.3.2", "3.2.3.3",
    # 4. Practical Guidance
    "4.1", "4.1.1", "4.1.2",
    "4.2", "4.2.1", "4.2.2",
    "4.3",
    "4.4", "4.4.1", "4.4.1.1", "4.4.1.2",
    "4.5", "4.6",
    # 5. Integrating Security into Development Processes
    "5.1",
    "5.2", "5.2.1", "5.2.2", "5.2.3", "5.2.4", "5.2.5",
    "5.3",
    # 6. Common AppSec Anti-Patterns
    "6.1", "6.1.1", "6.1.2", "6.1.3",
    "6.2", "6.2.1", "6.2.2",
    "6.3",
    # 7. Roles and Responsibilities
    "7.1", "7.1.1", "7.1.2", "7.1.3", "7.1.4", "7.1.5",
    "7.2", "7.3", "7.4",
    # 8. Organizational Adoption of FIASSE
    "8",
    "8.1", "8.1.1", "8.1.2", "8.1.3",
    "8.2", "8.2.1", "8.2.2", "8.2.3",
    # Appendix A. Measuring SSEM Attributes
    "A.1", "A.1.1", "A.1.2", "A.1.3", "A.1.4",
    "A.2", "A.2.1", "A.2.2", "A.2.3",
    "A.3", "A.3.1", "A.3.2", "A.3.3",
    "A.4",
]

# Map section_id -> regex pattern matching its starting heading in the framework.
# Headings may optionally be prefixed with 'S' (e.g. "## S2.1 ..." or "## 2.1.").
# The framework typically uses a trailing period after the section number.
HEADING_PATTERNS: dict[str, re.Pattern] = {
    sid: re.compile(
        rf"^#{{2,6}}\s+S?{re.escape(sid)}\.?\s",
        re.MULTILINE,
    )
    for sid in TARGET_SECTIONS
}

# Map section_id -> next sibling in TARGET_SECTIONS order. Used as the primary
# end-of-section marker.
_NEXT_SECTION: dict[str, Optional[str]] = {}
for i, sid in enumerate(TARGET_SECTIONS):
    _NEXT_SECTION[sid] = TARGET_SECTIONS[i + 1] if i + 1 < len(TARGET_SECTIONS) else None

# Higher-level chapter headings that terminate a section. Matches "## N.\s"
# or "### N.\s" for chapters 1-10, plus the Appendix A heading.
_CHAPTER_HEADS = [
    re.compile(rf"^#{{2,3}}\s+S?{ch}\.\s", re.MULTILINE)
    for ch in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
]
_APPENDIX_HEAD = re.compile(r"^#{2,3}\s+Appendix\s+A[:\s]", re.MULTILINE)


def _find_heading(content: str, section_id: str, start: int = 0) -> Optional[int]:
    """Return the character offset of the heading for section_id, or None."""
    pat = HEADING_PATTERNS.get(section_id)
    if not pat:
        return None
    m = pat.search(content, start)
    return m.start() if m else None


def _section_top(section_id: str) -> str:
    """Return the top-level chapter identifier ('A' for appendix sections)."""
    return section_id.split(".")[0]


def _find_section_end(content: str, section_id: str, body_start: int) -> int:
    """
    Find where a section ends. It ends at the start of the next target section's
    heading, or at a higher-level chapter heading, whichever comes first.
    """
    candidates: list[int] = []

    # Next section in our ordered list.
    nxt = _NEXT_SECTION.get(section_id)
    if nxt:
        pos = _find_heading(content, nxt, body_start)
        if pos is not None:
            candidates.append(pos)

    top = _section_top(section_id)

    # Numeric chapter heads. Only count if it's a different chapter from the
    # current section.
    for pat in _CHAPTER_HEADS:
        m = pat.search(content, body_start)
        if m:
            heading_text = content[m.start():m.end()]
            heading_num = re.search(r"(\d+)\.", heading_text)
            if heading_num and heading_num.group(1) != top:
                candidates.append(m.start())

    # Appendix A heading terminates any non-appendix section.
    if top != "A":
        m = _APPENDIX_HEAD.search(content, body_start)
        if m:
            candidates.append(m.start())

    return min(candidates) if candidates else len(content)


def extract_sections(content: str) -> list[tuple[str, str]]:
    """
    Parse FIASSE framework markdown into (section_id, body) tuples.
    Returns only sections listed in TARGET_SECTIONS.
    """
    results: list[tuple[str, str]] = []
    for sid in TARGET_SECTIONS:
        start = _find_heading(content, sid)
        if start is None:
            print(f"  WARNING: heading for section {sid} not found", file=sys.stderr)
            continue
        end = _find_section_end(content, sid, start + 1)
        body = content[start:end].strip()
        results.append((sid, body))
    return results


def _build_frontmatter(section_id: str) -> str:
    """Build YAML frontmatter for a section file."""
    meta = SECTION_META.get(section_id, {})
    title = meta.get("title", f"Section {section_id}")
    fm_id = f"S{section_id}"

    lines = [
        "---",
        f'title: "S{section_id} {title}"',
        f'fiasse_section: "{fm_id}"',
        'fiasse_version: "1.1"',
    ]

    if "ssem_pillar" in meta:
        lines.append(f'ssem_pillar: "{meta["ssem_pillar"]}"')

    if "ssem_attributes" in meta:
        lines.append("ssem_attributes:")
        for attr in meta["ssem_attributes"]:
            lines.append(f"  - {attr}")

    if "when_to_use" in meta:
        lines.append("when_to_use:")
        for item in meta["when_to_use"]:
            lines.append(f"  - {item}")

    if "threats" in meta:
        lines.append("threats:")
        for item in meta["threats"]:
            lines.append(f"  - {item}")

    if "summary" in meta:
        lines.append(f'summary: "{meta["summary"]}"')

    lines.append("---")
    return "\n".join(lines)


def extract(source_path: Path, dest_dir: Path) -> list[Path]:
    """
    Read source_path, extract sections, write each to dest_dir with YAML
    frontmatter. Returns paths of written files.
    """
    if not source_path.is_file():
        raise FileNotFoundError(f"Not a file: {source_path}")

    text = source_path.read_text(encoding="utf-8")
    sections = extract_sections(text)

    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for section_id, body in sections:
        frontmatter = _build_frontmatter(section_id)
        out_path = dest_dir / f"S{section_id}.md"
        content = f"{frontmatter}\n\n{body}\n"
        out_path.write_text(content, encoding="utf-8")
        written.append(out_path)
    return written


def main() -> None:
    if len(sys.argv) < 2:
        print(
            textwrap.dedent("""\
            Usage: extract_fiasse_sections.py <source.md> [dest_dir]

              source.md  Path to FIASSE framework markdown file (v1.1+).
              dest_dir   Output directory (default: data/fiasse).

            Download the v1.1 framework:
              curl -o /tmp/securable_framework.md \\
                https://raw.githubusercontent.com/OWASP/FIASSE/refs/tags/v1.1/docs/securable_framework.md
              python scripts/extract_fiasse_sections.py /tmp/securable_framework.md data/fiasse/
            """),
            file=sys.stdout,
        )
        sys.exit(1)

    source = Path(sys.argv[1]).resolve()
    dest = (
        Path(sys.argv[2]).resolve()
        if len(sys.argv) > 2
        else Path("data/fiasse").resolve()
    )

    try:
        paths = extract(source, dest)
        for p in paths:
            print(p)
        print(f"Wrote {len(paths)} section(s) to {dest}", file=sys.stderr)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
