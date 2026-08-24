# ASVS 5.0 Reference Data

80 structured ASVS 5.0 section files sourced from the [OWASP Agent Skills Project](https://github.com/eoftedal/owasp-agent-skills-project) by Erlend Oftedal.

## Source & License

These files are from `references/ASVS/` in the OWASP Agent Skills Project. OWASP ASVS is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

## File Format

Each file has YAML frontmatter with:

```yaml
---
title: "V6.2 Password Security"
asvs_chapter: "V6.2"
when_to_use:                          # Task-matching triggers
  - implementing password-based login
  - storing or verifying user passwords
threats:                              # Relevant threat categories
  - password cracking via weak hashing
  - credential stuffing
summary: "Requirements for securely handling user passwords."
---
```

Followed by the ASVS section content with requirements in a table:

```
| # | Description | Level |
| 6.2.1 | Verify that... | 1 |
```

Level indicates ASVS assurance level (1 = baseline, 2 = standard, 3 = advanced).

## Usage in Skills

### Code Review (`/code-review-security`)

When a finding maps to an ASVS section, reference the specific requirement:

```markdown
- **OWASP Ref**: ASVS V6.2.1
```

### Task-Based Lookup

Use the `when_to_use` frontmatter to match tasks to relevant ASVS sections. For example, if reviewing code that handles file uploads, check:
- `V5.1` — File Handling Documentation
- `V5.2` — File Upload and Content
- `V5.3` — File Storage

## Chapter Index

> **ASVS 5.0 renumbered its chapters.** The index below is derived from the `title` frontmatter of the files in this directory and is the authoritative mapping for this plugin. Do **not** use pre-5.0 chapter numbers (in ASVS 4.x, V2 was Authentication and V4 was Access Control — in 5.0 those topics live in V6 and V8).

| Chapter | Topic | Sections |
|---------|-------|----------|
| V1 | Encoding and Sanitization | V1.1-V1.5 |
| V2 | Validation and Business Logic (incl. Anti-automation) | V2.1-V2.4 |
| V3 | Web Frontend Security (cookies, headers, origin separation) | V3.1-V3.7 |
| V4 | API and Web Service (incl. GraphQL, WebSocket) | V4.1-V4.4 |
| V5 | File Handling | V5.1-V5.4 |
| V6 | Authentication (passwords, MFA, recovery) | V6.1-V6.8 |
| V7 | Session Management | V7.1-V7.6 |
| V8 | Authorization | V8.1-V8.4 |
| V9 | Self-contained Tokens (JWT etc.) | V9.1-V9.2 |
| V10 | OAuth and OIDC | V10.1-V10.7 |
| V11 | Cryptography | V11.1-V11.7 |
| V12 | Secure Communication (TLS) | V12.1-V12.3 |
| V13 | Configuration (incl. Secret Management) | V13.1-V13.4 |
| V14 | Data Protection | V14.1-V14.3 |
| V15 | Secure Coding and Architecture (incl. Dependencies, Concurrency) | V15.1-V15.4 |
| V16 | Security Logging and Error Handling | V16.1-V16.5 |
| V17 | WebRTC | V17.1-V17.3 |

## Updating

To refresh from upstream:

```bash
cd /tmp && git clone --depth 1 https://github.com/eoftedal/owasp-agent-skills-project.git
cp /tmp/owasp-agent-skills-project/references/ASVS/*.md data/asvs/
```
