---
inclusion: always
---
# Project structure & architecture

Hexagonal (ports & adapters). **Pure core, imperative shell.** Core never imports boto3, httpx, fastapi,
mcp, strands, or touches the filesystem/network/clock directly — those arrive through ports.

```
src/honeypass/
  core/           # PURE domain: models (Passport, Visa, Verdict, Finding, Trace), canonical hashing,
                  # verdict rules, visa matching. 100% unit + property tested. No I/O.
  ports.py        # Protocols: Signer, PassportStore, Sandbox, Clock, TraceSink
  inspect/        # Static Inspection: manifest/SKILL.md/mcp.json checks -> list[Finding]
  detention/      # Detention Room: honeypot tools, canary factory, Strands agent runner, trace capture
  guard/          # Border Guard: hook entrypoint (stdin JSON -> allow/block), passport + visa checks
  signing/        # Adapters: local_ecdsa.py, aws_kms.py (both implement Signer)
  store/          # Adapters: file_store.py, dynamodb_store.py (both implement PassportStore)
  mcp_server/     # FastMCP server exposing honeypass_* tools
  dashboard/      # FastAPI "Border Control" UI + SSE
  cli.py          # typer entrypoint: `honeypass inspect|detonate|passport|verify|guard`
  settings.py     # pydantic-settings
  errors.py       # HoneyPassError hierarchy
tests/
  unit/           # fast, no network, no AWS
  property/       # Hypothesis properties, one file per spec (e.g. test_passport_properties.py)
  integration/    # marked `integration`; may use Docker/localhost
  fixtures/plugins/
    benign-*/          # well-behaved sample plugins
    inert-hostile-*/   # clearly-labelled INERT hostile samples (localhost sink only)
powers/honeypass/      # HoneyPass itself packaged as an Agent Plugins 1.0 Power
docs/adr/              # Architecture Decision Records (NNNN-title.md)
docs/SPEC_PROMPTS.md   # ordered prompts used to create each Kiro spec
docs/LESSON_MAP.md     # living map: Kiro lesson -> files -> demo timestamp (for submission form)
```

## Rules
- New module? It must fit one of the folders above; otherwise propose an ADR first.
- Dependencies point inward: adapters -> ports -> core. Never core -> adapter.
- Each spec in `.kiro/specs/<name>/` maps to one package folder where possible.
- Record every significant decision (signing algorithm, sandbox choice, store) as an ADR.
