# HoneyPass — Spec Mode Prompt Playbook

Kiro generates `requirements.md → design.md → tasks.md` for each spec. Paste each prompt below into a
**new Spec session** (Kiro panel → Specs → **+**), in order. Review and edit every generated document
before approving it. That iteration is the "spec-driven development" judges want to see.

**Rules for every spec**
1. Create the branch first: `git switch -c feat/<spec-name>`.
2. Commit the approved spec documents in their own commit: `docs(kiro): add <spec-name> spec`.
3. Run tasks one at a time (or use the `spec-builder` custom agent). One commit per task.
4. Merge to `main` with a PR once the spec is done. Tag milestones.

| # | Spec name | When | Why it matters |
|---|---|---|---|
| 0 | *(no spec: steering review)* | Day 1 | Kiro checks our steering for gaps |
| 1 | `passport-core` | Sep 23–24 | Heart of the product; best property-based-testing showcase |
| 2 | `static-inspection` | Sep 24–26 | First real detections |
| 3 | `border-guard` | Sep 26–Oct 1 | Hooks lesson plus the rug-pull demo moment |
| 4 | `detention-room` | Oct 2–3 | The "wow": honeypot detonation on Bedrock |
| 5 | `honeypass-mcp-power` | Oct 3 | MCP and Powers lessons |
| 6 | `border-control-dashboard` | Oct 4 | The visuals for the video |
| 7 | `final-exam-adapter` | After Sep 25 prompt | Satisfies the official Final prompt |

---

## Prompt 0 — Steering review (normal chat, not Spec mode)

```text
Read every file in .kiro/steering/ plus pyproject.toml. Act as a principal engineer reviewing our project
standards for HoneyPass (see product.md). List contradictions, gaps, or anything outdated for a Python 3.13
enterprise codebase in September 2026, then propose concrete edits. Do not change files until I approve.
Also confirm which steering files load always vs fileMatch vs auto vs manual.
```

---

## Prompt 1 — `passport-core`

```text
Create a spec named "passport-core" for HoneyPass (see #product and #structure steering).

Goal: the pure domain core that turns a plugin directory into a signed, verifiable Passport.

Scope:
1. Plugin model: parse an Agent Plugins 1.0 package (plugin.json with $schema + name, optional mcp.json,
   skills/<name>/SKILL.md one level deep, optional dev.kiro/). Also support a bare Agent Skill folder
   and a standalone Kiro .kiro/settings/mcp.json entry as "plugin kinds".
2. Canonical content hash: deterministic SHA-256 over the plugin's files. Sorted relative POSIX paths,
   normalised line endings for text, excludes .git and OS junk, hard size limits (max files, max bytes),
   symlinks rejected, path traversal rejected.
3. Passport data model: plugin name, kind, content hash, verdict (CLEARED | DETAINED | DEPORTED |
   NEEDS_REVIEW), visa (allowed tools, path globs, egress domains), findings summary, issuer id,
   issued_at, expires_at, schema version. Canonical JSON serialisation for signing.
4. Signer port with a local ECDSA P-256/SHA-256 adapter (cryptography lib). Keep the port compatible with
   a later AWS KMS ECC_NIST_P256 adapter. Verify function returns a structured result
   (valid, reason), never raises for an invalid signature.
5. PassportStore port with a file-based adapter under HONEYPASS_DATA_DIR (default .honeypass/).
6. Visa matching: decide whether a proposed tool call (tool name, paths, domains) is inside a visa.

Requirements must use EARS with numbered IDs and include error cases (malformed plugin.json, missing
name, oversized plugin, symlink, traversal, expired passport, wrong key).

In design.md include a "Correctness Properties" section. At minimum:
- P1 Round-trip: for any valid passport p, verify(sign(p)) is valid.
- P2 Tamper-evidence: changing any byte of any plugin file changes the content hash, and verification
  against the old passport reports "hash_mismatch".
- P3 Determinism: hashing is independent of file creation order and platform line endings.
- P4 Serialisation round-trip: parse(serialise(p)) == p.
- P5 Visa containment: a tool call is allowed iff every path matches an allowed glob and every
  domain is allowed. Adding a permission never turns an allowed call into a denied one (monotonicity).
- P6 Expiry: any passport with expires_at <= now is never valid.
Each property must become one Hypothesis test in tests/property/test_passport_core_properties.py with
custom strategies (plugins(), passports(), tool_calls()).

Non-goals: no AWS, no network, no CLI, no UI in this spec. Record the signing-algorithm choice as ADR 0002.
```

---

## Prompt 2 — `static-inspection`

```text
Create a spec named "static-inspection" for HoneyPass. It depends on passport-core.

Goal: static Inspection of a plugin, producing a list of Findings (id, title, severity
INFO/LOW/MEDIUM/HIGH/CRITICAL, file, line, evidence snippet with secrets redacted, category, remediation)
and a preliminary verdict.

Detections (each needs a finding id like HP-INS-001 and at least one inert fixture that triggers it):
1. Manifest validity against Agent Plugins 1.0: closed plugin.json fields, name rules, skill folder name
   must equal SKILL.md frontmatter name, skills discovered one level deep only.
2. Hidden instructions: zero-width characters, bidi overrides, homoglyph-heavy text, HTML comments or
   base64 blobs inside SKILL.md.
3. Prompt-injection phrasing aimed at the host agent (ignore previous instructions, read credentials,
   modify steering/hooks, disable approvals). Use a transparent, explainable rule set, not a black box.
4. Risky capabilities: scripts calling network tools, reading home-directory secret paths, persistence
   (cron, shell rc files), writing outside the workspace.
5. MCP config risks: autoApprove on write/shell/network tools (these can bypass PreToolUse gates),
   unpinned `npx -y`/`uvx` package versions, remote servers over plain http, env values that look like
   secrets.
6. Map each finding to a category of the OWASP Agentic Skills Top 10. Fetch the current list with the
   fetch MCP server and cite the exact category names. Do not invent categories.

Fixtures: use the red-team custom agent to generate INERT fixtures in
tests/fixtures/plugins/inert-hostile-*/ plus 3 benign fixtures in tests/fixtures/plugins/benign-*/.

Correctness Properties to include:
- P1 Invisible-ink: inserting any zero-width or bidi-override character into any benign SKILL.md
  always produces a finding of severity >= HIGH.
- P2 No false positives on benign corpus: all benign fixtures produce no finding above LOW.
- P3 Redaction: no finding's evidence ever contains a string matching HONEYPASS-CANARY or an AWS key pattern.
- P4 Monotonicity: adding a hostile file to a plugin never lowers the maximum severity.
- P5 Robustness: for any random bytes as file content, inspection never raises; it returns findings or a
  "unparseable" finding.

Expose inspection as a pure function plus a thin `honeypass inspect <path>` typer CLI command with a
rich terminal table and a `--json` flag.
```

---

## Prompt 3 — `border-guard`

```text
Create a spec named "border-guard" for HoneyPass. It depends on passport-core.

Goal: the product-grade runtime Border Guard used as a Kiro PreToolUse hook command
(`uv run honeypass guard`). It reads the hook event JSON on stdin (hook_event_name, tool_name,
tool_input, cwd) and exits 0 to allow or 2 to block (stderr goes back to the agent).
It replaces the dev-time script in .kiro/hooks/scripts/border_guard.py while keeping its protections.

Behaviour:
1. Map MCP tool calls to their plugin (server name → installed plugin directory from .kiro/settings/mcp.json
   and installed Powers) and require a valid, unexpired CLEARED passport.
2. Rug-pull detection: recompute the plugin's content hash at call time (with a short cache keyed on file
   mtimes) and block on mismatch with a clear message naming the changed files.
3. Visa enforcement: block paths/domains outside the plugin's visa.
4. Lethal-trifecta session tracker: persist per-session state in .honeypass/sessions/. If a session has
   (a) read private data (secret paths / canaries), (b) ingested untrusted content (web fetch or untrusted
   plugin output), and now (c) attempts external communication, block and explain.
5. autoApprove audit: `honeypass guard --audit` lists MCP servers whose tools are in autoApprove
   (these bypass PreToolUse) and prints the fix.
6. Performance: p95 decision under 150 ms for cached plugins. Fail mode configurable (open/closed).
7. Every decision is appended to .honeypass/border-log.jsonl (no secrets) for the dashboard.

Correctness Properties:
- P1 Rug pull: for any passported plugin and any single-file modification, the next guarded call from
  that plugin is blocked with reason "hash_mismatch".
- P2 Canary escape: for any path string that resolves to a protected path (generated with ../, ~,
  URL-encoding, mixed case, duplicate slashes, unicode lookalikes), the decision is BLOCK.
- P3 Trifecta: for any ordering of events containing all three trifecta legs, the external-communication
  call is blocked. Any sequence missing a leg is not blocked for trifecta reasons.
- P4 Determinism: same event + same state ⇒ same decision.
- P5 Totality: for any JSON value on stdin, the guard exits with 0, 1 or 2 and never crashes.

Update .kiro/hooks/border-guard.json to call the new command once all tasks pass (keep the old script as fallback).
```

---

## Prompt 4 — `detention-room`

```text
Create a spec named "detention-room" for HoneyPass. It depends on passport-core and static-inspection.
Use the AWS Documentation MCP server and the Strands SDK power/docs to confirm current APIs before design.

Goal: behavioural detonation. Load a candidate skill/power into an isolated agent that has only
HONEYPOT tools, give it a benign task, record every tool call, and derive a verdict.

Design constraints:
1. Agent: Strands Agents on Amazon Bedrock; model id from HONEYPASS_BEDROCK_MODEL_ID; max turns, token and
   wall-clock limits; the candidate SKILL.md is injected as the skill under test.
2. Honeypot tools (no real side effects): fake filesystem (in-memory, seeded with canaries such as
   fake ~/.aws/credentials and .env containing HONEYPASS-CANARY-<uuid>), fake shell that records commands
   and returns plausible canned output, HTTP tool that only records requests (the "sink"), fake git.
3. Canary factory: unique canary per detonation so any leak is attributable.
4. Trace model: ordered steps (tool, args with canaries tokenised, timestamp). Store as JSONL locally;
   S3 in aws mode.
5. Verdict engine: apply the rules from the honeypass-triage skill (DEPORTED > DETAINED > NEEDS_REVIEW >
   CLEARED) and propose a visa from observed benign behaviour.
6. Sandboxes via a Sandbox port: `local` (in-process honeypot tools, default), `docker` (network=none plus
   sink sidecar), `agentcore` (AgentCore Runtime; optional, behind a flag, documented as stretch).
7. Deterministic test mode: a scripted fake model so detonations are testable without Bedrock.
8. Limitations section: sandbox-aware and time-delayed payloads may evade detonation; say so in reports.

Correctness Properties:
- P1 Containment: for any scripted tool-call sequence, no honeypot tool ever performs real filesystem
  writes outside a temp dir or real network I/O.
- P2 Attribution: any trace containing a canary value in an outbound request yields DEPORTED.
- P3 Verdict ordering: the verdict equals the maximum severity rule matched, independent of step order.
- P4 Redaction: serialised traces never contain raw canary values.
Also include an integration test (marked integration) that detonates the inert-hostile fixtures and the
benign fixtures with the scripted model and asserts expected verdicts.
```

---

## Prompt 5 — `honeypass-mcp-power`

```text
Create a spec named "honeypass-mcp-power". Follow MCP server best practices: tool names prefixed
honeypass_, pydantic input models with field descriptions and examples, structured JSON output plus a
short markdown summary, actionable error messages, and tool annotations (readOnlyHint, destructiveHint,
idempotentHint, openWorldHint).

1. FastMCP stdio server `honeypass-mcp` (add [project.scripts] entry) with tools:
   honeypass_inspect_plugin(path_or_git_url), honeypass_detonate_plugin(path, task?),
   honeypass_issue_passport(path), honeypass_verify_passport(path), honeypass_list_passports(),
   honeypass_audit_autoapprove().
   Git URLs are cloned shallowly into a temp dir with size limits; never executed.
2. Package HoneyPass as an Agent Plugins 1.0 Power in powers/honeypass/ (plugin.json closed schema,
   skills/honeypass-inspect/SKILL.md, mcp.json using ${PLUGIN_DATA} for writable state, dev.kiro/ steering).
   Add a validation test that checks the package against the spec rules (closed manifest fields, skill name
   equals folder name, no paths outside the package).
3. Enable the honeypass server in .kiro/settings/mcp.json (keep autoApprove empty) and make the
   customs-officer custom agent use it.
4. Document testing with the MCP Inspector.

Correctness Properties:
- P1 Tool results always validate against their declared output schema.
- P2 honeypass_verify_passport is read-only and idempotent: repeated calls return identical results and
  never modify the store.
```

---

## Prompt 6 — `border-control-dashboard`

```text
Create a spec named "border-control-dashboard". Use the frontend quality bar of a polished product demo.

A FastAPI app (`honeypass dashboard`) showing:
1. Live feed (server-sent events) of Border Guard decisions and Detention Room steps from
   .honeypass/border-log.jsonl and trace files.
2. Passport wall: each plugin as a passport card with an animated stamp (CLEARED green, DETAINED amber,
   DEPORTED red, NEEDS_REVIEW grey), content hash, visa, issued/expiry.
3. Detention replay: step-by-step timeline of a detonation; canary touches glow red; the exfil attempt
   to the sink is highlighted.
4. Accessible (keyboard, contrast AA), dark theme, no external CDNs at runtime.
Server-rendered HTML with vanilla JS or HTMX; no build step. Include snapshot-style tests for the JSON
endpoints and one property: for any log line sequence the feed endpoint never emits raw canary values.
```

---

## Prompt 7 — `final-exam-adapter` (write after the Final prompt is published Sep 25)

```text
Here is the official Kiro University Final prompt: <PASTE PROMPT>.
Create a spec named "final-exam-adapter" that satisfies every stated requirement of this prompt by building
on HoneyPass without breaking the core demo. First produce a requirements matrix: prompt requirement →
HoneyPass component → gap → task. Keep scope to what fits by 2026-10-04 and mark stretch items.
```

---

## Handy chat prompts (outside Spec mode)

- **Threat model:** `Using #security-policy and #product, write a STRIDE threat model for HoneyPass itself (the guard, the MCP server, the Detention Room). Save it as docs/threat-model.md.`
- **Custom agent use:** switch to `customs-officer` → `Inspect tests/fixtures/plugins/inert-hostile-exfil and give me the verdict report.`
- **Red team:** switch to `red-team` → `Create an inert fixture imitating a rug pull: a benign skill whose v2 adds a canary read.`
- **Release:** switch to `release-captain` → `Prepare v0.5.0: changelog, tag plan, LESSON_MAP update.`
