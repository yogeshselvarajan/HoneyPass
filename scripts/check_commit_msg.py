#!/usr/bin/env python3
"""commit-msg hook: enforce Conventional Commits 1.0 with HoneyPass scopes."""

import re
import sys
from pathlib import Path

TYPES = "feat|fix|test|refactor|perf|docs|build|ci|chore|revert"
SCOPES = "core|inspect|detention|guard|signing|store|mcp|dashboard|cli|power|kiro|deps"
PATTERN = re.compile(rf"^({TYPES})(\(({SCOPES})\))?!?: .{{1,72}}$")


def main() -> int:
    """Validate the first line of the commit message file passed by git."""
    first = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()[0].strip()
    if first.startswith(("Merge ", "Revert ", "fixup!", "squash!")) or PATTERN.match(first):
        return 0
    print(f"✗ Commit message must follow Conventional Commits: '{first}'", file=sys.stderr)
    print(f"  Format: <type>(<scope>): <summary ≤72>  types: {TYPES}", file=sys.stderr)
    print(f"  scopes: {SCOPES}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
