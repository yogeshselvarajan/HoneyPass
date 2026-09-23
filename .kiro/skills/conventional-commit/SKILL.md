---
name: conventional-commit
description: Write Conventional Commit messages and PR descriptions for the HoneyPass repo with Spec/Task/Refs trailers. Use after finishing a spec task or before opening a pull request.
---
# Conventional commit for HoneyPass

1. Inspect the staged diff (`git diff --staged --stat`, then the relevant hunks).
2. Pick exactly one type: feat, fix, test, refactor, perf, docs, build, ci, chore, revert.
3. Pick one scope: core, inspect, detention, guard, signing, store, mcp, dashboard, cli, power, kiro, deps.
4. Summary: imperative mood, ≤ 72 chars, no trailing period. Example: `feat(core): add canonical plugin hashing`.
5. Body (wrap at 72): why this change exists and any trade-off. Skip if trivial.
6. Trailers (required for spec work):
   ```
   Spec: <spec-name>
   Task: <task-number>
   Refs: R<id>, R<id>
   ```
7. Breaking change → add `!` after scope and a `BREAKING CHANGE:` footer.

## PR description template
- **What**: one paragraph.
- **Spec / requirements**: link `.kiro/specs/<name>/` + IDs covered.
- **Correctness properties tested**: P-ids and test names.
- **Kiro lessons demonstrated**: e.g. hooks, steering, MCP.
- **How to verify**: exact commands.
