#!/usr/bin/env python3
"""Normalise `.kiro` JSON files to UTF-8 without BOM, then validate them.

Windows PowerShell writes text as UTF-8-with-BOM (or UTF-16 with `Out-File`), which
`json.load(open(path))` cannot parse: it fails with "Expecting value: line 1 column 1".
Third-party setup scripts that generate hook files this way leave the workspace with hooks
Kiro silently refuses to load. Running this makes the repo self-healing after such a script.

Usage:
    python scripts/fix_hook_encoding.py           # fix in place, exit 1 if any file stays broken
    python scripts/fix_hook_encoding.py --check    # report only, never write
    python scripts/fix_hook_encoding.py --quiet    # report only changes/failures, always exit 0
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path

# Byte-order marks PowerShell redirection produces, longest first so UTF-32 wins over UTF-16.
# The codecs are the BOM-aware variants, which detect endianness and drop the mark on decode.
BOMS: tuple[tuple[bytes, str], ...] = (
    (b"\xff\xfe\x00\x00", "utf-32"),
    (b"\x00\x00\xfe\xff", "utf-32"),
    (b"\xef\xbb\xbf", "utf-8-sig"),
    (b"\xff\xfe", "utf-16"),
    (b"\xfe\xff", "utf-16"),
)

# Globs are relative to the repo root; every match must be JSON that Kiro can load.
# `.kiro/*.json` matters as much as the hooks: the Kironomics reporter parses `.kiro/ugmdu.json`
# with `json.loads(path.read_text())` inside a bare `except Exception: return {}`, so a BOM there
# silently drops campaign attribution instead of failing loudly.
TARGET_GLOBS: tuple[str, ...] = (
    ".kiro/*.json",
    ".kiro/hooks/*.json",
    ".kiro/hooks/scripts/*.json",
    ".kiro/agents/*.json",
    ".kiro/settings/*.json",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class Result:
    """Outcome of inspecting one file."""

    ok: bool
    """False only when the file still does not parse as JSON."""
    changed: bool
    """True when a BOM was found (and stripped, unless running in --check mode)."""
    note: str
    """Human-readable one-line explanation."""


def detect_bom(raw: bytes) -> str | None:
    """Return the encoding implied by a leading BOM, or None when there is no BOM."""
    for bom, encoding in BOMS:
        if raw.startswith(bom):
            return encoding
    return None


def normalise(path: Path, *, write: bool) -> Result:
    """Rewrite one file as UTF-8 without BOM and validate that it parses as JSON.

    Args:
        path: File to inspect.
        write: When False, only report what would change.

    Returns:
        The inspection result for `path`.
    """
    raw = path.read_bytes()
    encoding = detect_bom(raw)
    note = "already utf-8, no byte-order mark"
    if encoding is not None:
        # removeprefix guards the case where a codec leaves U+FEFF in the decoded text.
        text = raw.decode(encoding).removeprefix("\ufeff")
        verb = "stripped" if write else "would strip"
        note = f"{verb} byte-order mark ({encoding})"
        if write:
            # newline="" keeps the file's own line endings so git sees a minimal diff.
            path.write_text(text, encoding="utf-8", newline="")
            raw = path.read_bytes()
    changed = encoding is not None
    try:
        json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as err:
        return Result(ok=False, changed=changed, note=f"{note}; still invalid JSON: {err}")
    return Result(ok=True, changed=changed, note=note)


def main() -> int:
    """Normalise every target file and report a one-line status for each.

    Returns:
        0 when every file parses, or when `--quiet` is set (advisory mode for SessionStart,
        where a non-zero exit would make Kiro discard the stdout report). 1 otherwise.
    """
    args = sys.argv[1:]
    write, quiet = "--check" not in args, "--quiet" in args
    root = Path(__file__).resolve().parent.parent
    paths = sorted({p for glob in TARGET_GLOBS for p in root.glob(glob)})
    if not paths:
        if not quiet:
            print("no .kiro JSON files found - nothing to check")
        return 0
    failed = 0
    for path in paths:
        result = normalise(path, write=write)
        if not quiet or not result.ok or result.changed:
            mark = "ok  " if result.ok else "FAIL"
            print(f"{mark} {path.relative_to(root).as_posix()}: {result.note}")
        failed += not result.ok
    if failed:
        print(f"\n{failed} file(s) are not loadable JSON - fix them before running Kiro hooks.")
    return 1 if failed and not quiet else 0


if __name__ == "__main__":
    sys.exit(main())
