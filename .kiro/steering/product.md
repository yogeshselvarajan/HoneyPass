---
inclusion: always
---
# Product: HoneyPass — "Every AI skill needs a passport."

## One-liner
HoneyPass is customs & immigration for AI agent plugins (Kiro Powers, Agent Skills, MCP servers).
Scanners *read* a skill. HoneyPass *watches it act* — then issues a signed passport or detains it.

## Why now (context for design decisions)
- Kiro Powers follow the Agent Plugins 1.0 spec and can be installed from any GitHub URL.
- Agent Plugins 1.0 deliberately leaves out registries, sandboxing, permissions and provenance.
- Poisoned-skill campaigns (e.g. ClawHavoc on ClawHub) showed skills inherit the full permissions of the agent.
- Static scanners exist (Snyk agent-scan, Cisco mcp-scanner). Our differentiation is: **behavioural detonation
  + signed passports + runtime enforcement inside Kiro hooks + rug-pull detection**. Never claim we invented
  static scanning or sandboxing in general.

## The four stations (domain language — use these exact terms in code, docs and UI)
| Term | Meaning |
|---|---|
| **Inspection** | Static analysis of `plugin.json`, `SKILL.md`, `mcp.json`, scripts. |
| **Detention Room** | Sandboxed detonation: the candidate skill runs inside an instrumented agent with honeypot tools. |
| **Canary** | Fake secret (e.g. fake AWS credentials) planted in the Detention Room. Touching it = hostile intent. |
| **Passport** | Signed attestation: plugin content hash + verdict + visa + issuer + timestamps. |
| **Visa** | Declared permissions a plugin is allowed at runtime (tools, paths, egress domains). |
| **Border Guard** | Runtime `PreToolUse` enforcement that checks passports and visas before tool calls. |
| **Rug pull** | Plugin content changes after its passport was issued (hash mismatch). |
| **Verdict** | `CLEARED` \| `DETAINED` \| `DEPORTED` (hostile, permanently denied) \| `NEEDS_REVIEW`. |

## Users
1. Developers installing third-party Powers/skills into Kiro (primary).
2. Platform/security teams who want an allow-list of passported plugins (secondary).
3. Plugin authors who want a "HoneyPass CLEARED" badge (tertiary).

## Demo story (must always work end-to-end)
1. Install an **inert** "malicious" demo power → Inspection flags it → Detention Room shows canary read +
   exfil attempt to a **localhost** sink → `DETAINED` stamp.
2. Install a benign power → passport issued and signed → `CLEARED` stamp.
3. Silently modify the cleared power (rug pull) → Border Guard blocks its next tool call.

## Non-goals (do not build)
- Not a general antivirus, not a network firewall, not a replacement for Snyk/Cisco scanners.
- No real malware. All "malicious" fixtures are inert, clearly labelled, and only talk to localhost.
- No multi-tenant SaaS, billing, or user accounts in this hackathon scope.

## Challenge context
Built for the Kiro University Challenge (final due 2026-10-05 23:59 PT). Every feature should also make a
Kiro lesson visible (specs, steering, hooks, MCP, powers/skills, custom agents, property-based testing).
