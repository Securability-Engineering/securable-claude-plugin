---
title: "SA.4 Scoring and Enhancement Suggestions"
fiasse_section: "SA.4"
fiasse_version: "1.1"
ssem_pillar: "All"
ssem_attributes:
  - Analyzability
  - Modifiability
  - Testability
  - Observability
  - Confidentiality
  - Accountability
  - Authenticity
  - Availability
  - Integrity
  - Resilience
when_to_use:
  - combining SSEM indicators into a composite score
  - pairing a score with attribute-specific enhancement suggestions
  - reporting deltas against a prior scan so change is visible
  - deciding when a scored finding needs reviewer confirmation
threats:
  - a composite score mistaken for a statement of assurance or compliance
  - false precision from a single number standing in for posture
  - teams optimizing for the score at the expense of the architecture
summary: "A composite score is a directional management aid, not a statement of assurance. Useful for comparing a system against itself over time and for surfacing the weakest attributes first. Pair it with suggestions that are attribute-specific, actionable, evidence-based, comparable over time, context-aware, and reviewed when material. The most useful output has three parts: the score, the rationale, and prioritized changes."
---

### A.4. Scoring and Enhancement Suggestions

Where teams choose to combine SSEM indicators into a composite score, the score should be treated as a directional management aid, not as a statement of assurance, compliance, or absolute security. A score can help compare a system against itself over time and can help surface the weakest attributes first, but it should not be used to imply that the codebase is "secure" or that a single number captures the system's securable posture.

Scoring works best when it is paired with concrete enhancement suggestions that are specific to the attribute being measured. Those suggestions should be:

- **Attribute-specific:** Tie each recommendation to a named SSEM attribute or sub-attribute so the team knows what quality is being improved.
- **Actionable:** State the next engineering step, not just the deficiency. For example, "add boundary validation for external input" is more useful than "improve input handling."
- **Evidence-based:** Explain which metric, review finding, or observed behavior triggered the suggestion.
- **Comparable over time:** Report deltas against prior scans so teams can see whether a change improved or degraded the relevant attribute.
- **Context-aware:** Distinguish between a systemic weakness and a local exception so teams do not optimize for the score at the expense of the architecture.
- **Reviewed when material:** For high-impact systems or significant drops in score, require a reviewer to confirm that the suggested change is appropriate before it becomes a development commitment.

The most useful scoring outputs therefore include three parts: the score itself, the rationale for the score, and a short list of prioritized changes that would improve the underlying attribute. This preserves the educational value of the framework while avoiding the false precision that can occur when a composite score is mistaken for a complete security judgment.
