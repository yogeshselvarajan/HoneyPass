# Getting started (do this in order)

## 1. Create the repo (today; first commit must be after Sep 21 09:00 PT, which has already passed)
```bash
cd honeypass
git init -b main
git config commit.template .gitmessage
uv sync --all-groups
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
bash .kiro/hooks/scripts/quality_gate.sh
git add .
git commit -m "chore(kiro): scaffold HoneyPass with steering, hooks, agents and MCP config"
gh repo create honeypass --public --source=. --push      # or create it on github.com and push
```
On GitHub, protect `main`: Settings → Branches → require PR + passing CI, and block force pushes.

## 2. Open in Kiro and verify everything loads
- **Steering**: 10 files in the Kiro panel (always: product, tech, structure, security-policy, git-workflow;
  fileMatch: python-standards, testing-standards, spec-authoring; auto: aws-standards; manual: submission).
- **Hooks**: border-guard, untrusted-artifacts, spec-flow, quality, session.
  Test the guard: ask Kiro to `read ~/.aws/credentials` and it should be BLOCKED.
- **MCP**: aws-docs, context7, fetch connected; honeypass stays disabled until spec 5.
- **Agents**: customs-officer, spec-builder, red-team, release-captain.
- On Windows, if `python3` isn't found, change the hook commands to `python` or `py -3`.

## 3. Install these Powers from the Kiro Powers panel (optional but useful)
- **Strands SDK** (Detention Room agent)
- Any AWS-focused powers you already use (e.g. the AWS Security Agent power, if your account has access)

## 4. Verify against current Kiro docs (formats change fast)
These are the parts I could not verify with certainty from the docs. Check them once in your Kiro version:
- Custom agent `tools` syntax for an MCP server (`"@honeypass"`), and permission `capability` names
  beyond `shell` → https://kiro.dev/docs/custom-agents/ and https://kiro.dev/docs/permissions/
- Hook event JSON fields in the IDE (`hook_event_name`, `tool_input`). The guard handles missing names.
- Workspace skills location `.kiro/skills/<name>/SKILL.md` → https://kiro.dev/docs/skills/

## 5. Build
Follow `docs/SPEC_PROMPTS.md` from Prompt 0. One branch per spec, one commit per task.
Keep `docs/LESSON_MAP.md` updated as each lesson is published.
