---
inclusion: fileMatch
fileMatchPattern: ["tests/**/*.py", "**/conftest.py"]
---
# Testing standards

## Layout & markers
- `tests/unit/` — fast, isolated, no network, no AWS, no Docker. Default test run.
- `tests/property/` — Hypothesis property tests. **Every "Correctness Property" in a spec's design.md must
  have exactly one property test**, named `test_prop_<spec>_<property_id>` with a docstring quoting the
  property and its requirement IDs (e.g. `Validates: R2.1, R2.3`).
- `tests/integration/` — `@pytest.mark.integration`; may use Docker/localhost.
- AWS tests — `@pytest.mark.aws`; use `moto` for unit-level AWS, real AWS only in integration and opt-in.

## Style
- Arrange / Act / Assert with blank lines between sections.
- Test names: `test_<unit>_<behaviour>_<condition>`.
- One behaviour per test. No logic (loops/ifs) in tests except in Hypothesis strategies.
- Use factories/builders in `tests/factories.py`, not copy-pasted dicts.
- Fixtures under `tests/fixtures/plugins/`; hostile fixtures must be **inert** and named `inert-hostile-*`.

## Hypothesis
- Profiles in `tests/conftest.py`: `dev` (max_examples=100) and `ci` (max_examples=500, derandomize=True).
- Write custom strategies for domain objects (`plugins()`, `passports()`, `tool_calls()`, `hostile_paths()`).
- When a property fails, add the shrunk example as an explicit `@example(...)` regression.

## Coverage & gates
- `src/honeypass/core` ≥ 95% line coverage; whole package ≥ 85%.
- Tests must pass before a spec task is marked complete.
