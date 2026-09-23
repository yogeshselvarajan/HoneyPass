---
inclusion: fileMatch
fileMatchPattern: ["**/*.py", "pyproject.toml"]
---
# Python engineering standards (enterprise, 2026)

## Language & typing
- Target Python 3.13. Use modern syntax: `X | None`, built-in generics (`list[str]`), `type` aliases,
  `typing.Self`, `typing.override`, `enum.StrEnum`, `match` for multi-branch dispatch on variants.
- **Every function is fully annotated**, including return types. `Any` is banned except at
  JSON/MCP boundaries, where it must be validated into a pydantic model immediately.
- `pyrefly check` must pass with zero errors. No `# type: ignore` without a trailing reason.
- Prefer `Protocol` for ports; prefer composition over inheritance.

## Design
- Pure core, imperative shell: domain logic takes values in and returns values out.
- Functions ≤ 40 lines, cyclomatic complexity ≤ 10, max 4 positional parameters (use keyword-only `*`).
- Domain objects: `@dataclass(frozen=True, slots=True, kw_only=True)`. Boundary DTOs: pydantic v2 `BaseModel`
  with `model_config = ConfigDict(frozen=True, extra="forbid")`.
- Dependency injection via constructor/function parameters. No module-level singletons except `get_settings()`
  (cached with `functools.cache`).
- Time: inject a `Clock`; never call `datetime.now()` in core. Always timezone-aware (`datetime.now(UTC)`).
- Paths: `pathlib.Path` only. Never string-concatenate paths.

## Errors
- All raised errors subclass `honeypass.errors.HoneyPassError`. Error messages must be actionable
  (what failed, why, what to do next).
- Never `except Exception:` without re-raising or logging with `log.exception`. Never bare `except:`.
- Use `raise ... from err` to keep causes.

## Logging & observability
- `structlog.get_logger(__name__)`; log events as `snake_case` event names with key-value context,
  e.g. `log.info("passport_issued", plugin=name, verdict=verdict)`.
- No `print()` outside `cli.py` user output (Ruff `T20` enforces this).
- Never log secrets, canary values, full file contents of untrusted plugins, or tokens.

## Security (Ruff `S` rules are on — treat as errors)
- No `eval`, `exec`, `pickle`, `marshal`, `yaml.load` (use `yaml.safe_load`), `shell=True`.
- `subprocess.run([...], check=True, timeout=...)` with list args only.
- Every network call has an explicit timeout. Every loop over untrusted input has a size/iteration cap.
- Compare signatures/hashes with `hmac.compare_digest`.
- Treat all plugin content as **untrusted data**: parse, never execute outside the Detention Room.
- Zip/tar extraction must prevent path traversal (validate every member path stays inside the target dir).

## Async
- Async only at I/O edges (MCP server, dashboard, Bedrock calls). Core stays sync and pure.
- No blocking calls inside `async def` (use `anyio.to_thread` if unavoidable).

## Docs & style
- Google-style docstrings on every public module, class, and function. Explain *why*, not *what*.
- Ruff formatter is the source of truth (line length 100). Imports sorted by Ruff (`I`).
- Names: modules `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE`, private `_leading_underscore`.
