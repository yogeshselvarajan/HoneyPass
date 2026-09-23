---
inclusion: always
---
# Tech stack & commands

## Runtime
- **Python 3.13** (pinned in `.python-version`; code must also run on 3.14). `src/` layout, package `honeypass`.
- **uv** is the only package/venv manager. Never use `pip install`, `poetry`, or `requirements.txt`.
  Add deps with `uv add <pkg>` / `uv add --dev <pkg>`; commit `uv.lock`.

## Approved libraries (ask before adding anything else)
| Purpose | Library |
|---|---|
| Domain models at boundaries (I/O, JSON, MCP inputs) | `pydantic` v2, `pydantic-settings` |
| Pure core domain objects | stdlib `dataclasses(frozen=True, slots=True)`, `enum.StrEnum` |
| CLI | `typer` |
| HTTP client | `httpx` (always with explicit timeouts) |
| Logging | `structlog` (JSON in CI/prod, console locally) |
| Crypto (passport signing) | `cryptography` — **ECDSA P-256 / SHA-256** locally, AWS KMS `ECC_NIST_P256` + `ECDSA_SHA_256` in cloud mode, so signatures are interchangeable |
| AWS | `boto3` (Bedrock Runtime, KMS, DynamoDB, S3) with `botocore.config.Config(retries={"mode": "adaptive"})` |
| Detention Room agent | `strands-agents` on Amazon Bedrock (model id from settings, never hard-coded) |
| MCP server | official `mcp` Python SDK (FastMCP) |
| Dashboard | `fastapi` + `uvicorn`, server-sent events for live traces; plain HTML/CSS/vanilla JS or HTMX (no heavy SPA) |
| Tests | `pytest`, `hypothesis`, `pytest-cov`, `moto` (AWS mocks) |
| Quality | `ruff` (format + lint), `pyrefly` (type checking, stable 1.0) |

## Commands (the agent should use exactly these)
| Task | Command |
|---|---|
| Install / sync | `uv sync --all-groups` |
| Format | `uv run ruff format .` |
| Lint (autofix) | `uv run ruff check --fix .` |
| Type check | `uv run pyrefly check` |
| Unit + property tests | `uv run pytest -m "not aws and not integration"` |
| All tests with coverage | `uv run pytest --cov=honeypass --cov-report=term-missing` |
| Full quality gate | `bash .kiro/hooks/scripts/quality_gate.sh` |

## Configuration
- All config via `honeypass.settings.Settings` (pydantic-settings), env prefix `HONEYPASS_`.
- Modes: `HONEYPASS_MODE=local` (file store + local ECDSA key + Docker/subprocess sandbox) and
  `HONEYPASS_MODE=aws` (DynamoDB + KMS + S3 traces + optional AgentCore Runtime). Local mode must work
  fully offline except for the Bedrock call.
- AWS region from `AWS_REGION`; profile from standard AWS env/SSO. Never read `~/.aws/credentials` directly.

## Live project files
#[[file:pyproject.toml]]
