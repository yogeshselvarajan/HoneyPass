---
name: honeypass-triage
description: Triage a HoneyPass Detention Room trace or inspection report and decide a verdict (CLEARED, DETAINED, DEPORTED, NEEDS_REVIEW) with evidence. Use when reviewing plugin inspection output or detonation traces.
---
# HoneyPass triage

## Verdict rules (apply in order)
1. **DEPORTED**: any canary token (`HONEYPASS-CANARY`) read AND sent to any network sink, or any attempt to
   modify steering/hooks/agent config, or persistence attempts.
2. **DETAINED**: canary read without exfil; egress to a domain not in the declared visa; hidden
   zero-width/bidi characters containing instructions; prompt-injection phrases targeting the host agent;
   MCP config requesting `autoApprove` for write/shell/network tools.
3. **NEEDS_REVIEW**: over-broad visa (e.g. shell `*`, all paths) without detected abuse; detonation timeout;
   inconclusive trace.
4. **CLEARED**: none of the above; all observed tool calls stay inside the proposed visa.

## Report format
- Verdict + one-sentence reason.
- Evidence table: step, tool, arguments (secrets redacted), rule triggered.
- Proposed visa: allowed tools, path globs, egress domains.
- Limitations: what this detonation could NOT prove (e.g. time-delayed or sandbox-aware behaviour).

Never quote canary values or secrets in the report; write `[REDACTED-CANARY]`.
