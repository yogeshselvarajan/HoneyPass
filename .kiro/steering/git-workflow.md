---
inclusion: always
---
# Git workflow

## Branching (GitHub Flow, short-lived branches)
- `main` is always green and demo-able. Never commit directly to `main`; never force-push `main`.
- One branch per spec: `feat/<spec-name>` (e.g. `feat/passport-core`). Other prefixes:
  `fix/<slug>`, `test/<slug>`, `docs/<slug>`, `chore/<slug>`, `ci/<slug>`, `spec/<spec-name>` (spec docs only).
- Branch lifetime ≤ 2 days. Rebase on `main` before opening a PR. Merge with **rebase-merge** so each
  Kiro task commit stays visible in history (judges can see spec → task → commit traceability).
- Tag milestones: `v0.1.0` (passport core), `v0.5.0` (detention room), `v1.0.0` (submission).

## Commits — Conventional Commits 1.0
Format: `<type>(<scope>): <imperative summary ≤ 72 chars>`
- Types: `feat`, `fix`, `test`, `refactor`, `perf`, `docs`, `build`, `ci`, `chore`, `revert`.
- Scopes: `core`, `inspect`, `detention`, `guard`, `signing`, `store`, `mcp`, `dashboard`, `cli`,
  `power`, `kiro` (anything under `.kiro/`), `deps`.
- Body: *why* the change was made. Footer trailers:
  ```
  Spec: passport-core
  Task: 3
  Refs: R1.2, R2.1
  ```
- **One commit per completed Kiro spec task.** Commit `.kiro/` changes (steering/hooks/agents/specs) in
  their own `docs(kiro): ...` or `chore(kiro): ...` commits so the evolution of the Kiro setup is visible.
- Never use `--no-verify`. Fix the hook failure instead.

## Pull requests
- Use `.github/pull_request_template.md`. Link the spec and list requirement IDs covered.
- CI (ruff, pyrefly, pytest) must pass before merge.

## Kiro University Challenge rules (hard constraints)
- Repo must be public and new; first commit after 2026-09-21 09:00 PT.
- **No commits after 2026-10-05 23:59 PT (2026-10-06 12:29 IST) until judging ends (~2026-10-19).**
  The border guard hook blocks `git commit`/`git push` inside that window.
- `.kiro/` must be committed (never add it to `.gitignore`).
