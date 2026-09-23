# Kiro lesson map (living document → copy into the submission form)

| Lesson | What we built | Evidence in repo | Demo video timestamp |
|---|---|---|---|
| 1. Spec-driven development | 6 specs with EARS requirements, design with correctness properties, test-first tasks | `.kiro/specs/*`, `docs/SPEC_PROMPTS.md` | |
| 2. Steering | 10 steering docs: always / fileMatch / auto / manual; live `#[[file:pyproject.toml]]` include | `.kiro/steering/*` | |
| Hooks | PreToolUse border guard (blocking), UserPromptSubmit secret block, PostFileCreate quarantine, Pre/PostTaskExec test-first flow, PostFileSave formatting, Stop quality gate with confirm | `.kiro/hooks/*` | |
| MCP | HoneyPass MCP server + AWS Docs, Context7, Fetch; no autoApprove by policy | `.kiro/settings/mcp.json`, `src/honeypass/mcp_server/` | |
| Powers / Skills | HoneyPass packaged as an Agent Plugins 1.0 Power; workspace skills | `powers/honeypass/`, `.kiro/skills/*` | |
| Custom agents | customs-officer (read-only), spec-builder, red-team (inert fixtures), release-captain | `.kiro/agents/*` | |
| Property-based testing | Hypothesis properties mapped to design.md P-ids | `tests/property/*` | |
| Bonus | *(fill in when bonus lessons are posted)* | | |

> Update this table as lessons 3–7 and bonuses are published (Sep 22–24) and remap if needed.
