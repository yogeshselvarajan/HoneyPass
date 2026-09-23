---
inclusion: fileMatch
fileMatchPattern: [".kiro/specs/**/*.md"]
---
# How we write Kiro specs

## requirements.md
- User stories + acceptance criteria in **EARS** notation: `WHEN <trigger> THE SYSTEM SHALL <response>`,
  `IF <condition> THEN THE SYSTEM SHALL ...`, `WHILE <state> ...`, `WHERE <feature> ...`.
- Number everything: `R1`, `R1.1`, `R1.2`. IDs are referenced by tasks, tests and commits.
- Include explicit error/edge-case criteria (malformed input, oversized input, missing files, timeouts).

## design.md
- Sections: Overview, Architecture (mermaid diagram), Components & Interfaces (ports), Data Models,
  **Correctness Properties**, Error Handling, Testing Strategy, Security Considerations.
- Correctness Properties: numbered `P1..Pn`, each a universally-quantified statement
  ("For any valid passport p, verify(sign(p)) is True") with `Validates: R…` links. These become Hypothesis tests.

## tasks.md
- Small tasks (≤ 1 hour each), ordered so the build is green after every task.
- Test-first: each implementation task is preceded or accompanied by its tests/property tests.
- Every task lists the requirement IDs it satisfies.
