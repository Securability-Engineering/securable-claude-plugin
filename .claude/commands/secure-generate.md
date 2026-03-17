Generate code that embodies securable qualities by default, applying FIASSE/SSEM principles as engineering constraints.

Use the skill definition in `skills/securability-engineering/SKILL.md` for attribute enforcement rules.
Reference `data/fiasse/` sections for detailed definitions when needed.

## Constraints Applied

Every piece of generated code is held to the nine SSEM attributes:

- **Analyzability** — Small methods (≤30 LoC), cyclomatic complexity < 10, clear naming, comments at trust boundaries
- **Modifiability** — Loose coupling, dependency injection, no static mutable state, centralized security logic
- **Testability** — All public interfaces testable, dependencies injectable/mockable
- **Confidentiality** — Sensitive data classified at the type level, no secrets in code/logs/errors, encryption where applicable
- **Accountability** — Structured audit logging for security-sensitive actions, no sensitive data in logs
- **Authenticity** — Established auth mechanisms, token/session integrity verification
- **Availability** — Resource limits, timeouts on external calls, rate limiting, graceful degradation
- **Integrity** — Input validation at trust boundaries (canonicalize → sanitize → validate), parameterized queries, Derived Integrity Principle
- **Resilience** — Defensive coding, specific exception handling, resource leak prevention, immutable data in concurrent code

## Trust Boundary Handling

Apply the Turtle Analogy: hard shell at trust boundaries, flexible interior. Identify all trust boundaries and apply strict input handling at every entry point.

## Arguments

- `$ARGUMENTS` — Description of what code to generate (e.g., "REST API endpoint for user registration", "file upload handler with validation").
