#!/usr/bin/env python3
"""HoneyPass dev-time border guard for Kiro hooks (PreToolUse and UserPromptSubmit).

Reads the hook event as JSON on stdin. Exit codes follow Kiro's hook contract:
  0 -> allow, 2 -> block (stderr is returned to the agent), other -> warning, allowed.

This is the *development-time* safety net that protects this workspace while HoneyPass
is being built. The product-grade Border Guard (passports, visas, rug-pull detection) is
specified in .kiro/specs/border-guard and lives in src/honeypass/guard/. Stdlib only, so it
runs without `uv sync`.

Only path-like and command-like fields of tool inputs are inspected, never file *content*, so the
agent can still write documentation that mentions sensitive paths.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

POLICY_FILE = Path(__file__).with_name("guard_policy.json")
EXIT_ALLOW, EXIT_BLOCK, EXIT_WARN = 0, 2, 1
MAX_STRINGS = 5_000
MAX_DEPTH = 20


def load_policy() -> dict[str, Any]:
    return json.loads(POLICY_FILE.read_text(encoding="utf-8"))


def iter_fields(obj: object, key: str = "", depth: int = 0) -> Iterator[tuple[str, str]]:
    """Yield (key, string) pairs from nested JSON, remembering the nearest key name."""
    if depth > MAX_DEPTH:
        return
    if isinstance(obj, str):
        yield key, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from iter_fields(v, str(k), depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_fields(item, key, depth + 1)


def normalize_path(raw: str) -> str:
    text = unquote(raw).replace("\\", "/").strip().strip("'\"")
    text = str(Path(text).expanduser())
    return os.path.normpath(text).replace("\\", "/")


def check_paths(paths: list[str], policy: dict[str, Any]) -> list[str]:
    reasons = []
    patterns = [re.compile(p, re.IGNORECASE) for p in policy["secret_path_patterns"]]
    for raw in paths:
        norm = normalize_path(raw)
        if norm.endswith((".example", ".sample", ".template")):
            continue
        if any(p.search(norm) for p in patterns):
            reasons.append(f"secret_path: access to '{raw}' is not allowed (security-policy.md)")
    return reasons


def tokens_as_paths(command: str) -> list[str]:
    return [
        t
        for t in re.split(r"[\s;&|<>()=]+", command)
        if "/" in t or t.startswith(".") or t.startswith("~")
    ]


def host_allowed(host: str, allowlist: list[str]) -> bool:
    host = host.lower().split(":")[0]
    return any(host == a or host.endswith("." + a) for a in allowlist)


def check_commands(commands: list[str], policy: dict[str, Any], now: datetime) -> list[str]:
    reasons: list[str] = []
    net_tool = re.compile(policy["network_tools_regex"], re.IGNORECASE)
    freeze = policy["freeze"]
    start, end = (
        datetime.fromisoformat(freeze["start_utc"]),
        datetime.fromisoformat(freeze["end_utc"]),
    )
    for cmd in commands:
        for name, pattern in policy["dangerous_command_patterns"]:
            if re.search(pattern, cmd, re.IGNORECASE):
                reasons.append(f"{name}: blocked command pattern in '{cmd[:120]}'")
        if net_tool.search(cmd) or cmd.lower().startswith(("http://", "https://")):
            for url in re.findall(r"https?://[^\s'\"<>|;]+", cmd):
                host = urlparse(url).hostname or ""
                if not host_allowed(host, policy["egress_allowlist"]):
                    reasons.append(f"egress: '{host}' is not on the egress allowlist")
        if start <= now < end and re.search(freeze["command_regex"], cmd):
            reasons.append(
                "challenge_freeze: no commits/pushes between Oct 5 23:59 PT and end of judging"
            )
        reasons.extend(check_paths(tokens_as_paths(cmd), policy))
    return reasons


def check_prompt(prompt: str, policy: dict[str, Any]) -> list[str]:
    return [
        f"{name}: the prompt appears to contain a secret; remove it and use env vars instead"
        for name, pattern in policy["prompt_secret_patterns"]
        if re.search(pattern, prompt)
    ]


def evaluate(event: dict[str, Any], policy: dict[str, Any], now: datetime) -> list[str]:
    event_name = str(event.get("hook_event_name", "")).lower()
    is_prompt_event = "prompt" in event_name and "tool" not in event_name
    if is_prompt_event or ("prompt" in event and "tool_input" not in event):
        return check_prompt(str(event.get("prompt", "")), policy)
    path_keys = {k.lower() for k in policy["path_keys"]}
    command_keys = {k.lower() for k in policy["command_keys"]}
    paths, commands = [], []
    for i, (key, value) in enumerate(iter_fields(event.get("tool_input", {}))):
        if i >= MAX_STRINGS:
            break
        if key.lower() in path_keys:
            paths.append(value)
        elif key.lower() in command_keys:
            commands.append(value)
    return check_paths(paths, policy) + check_commands(commands, policy, now)


def main() -> int:
    policy: dict[str, Any] = {"fail_mode": "open"}
    try:
        policy = load_policy()
        event = json.loads(sys.stdin.read() or "{}")
        reasons = evaluate(event, policy, datetime.now(UTC))
    except Exception as err:  # a broken guard must neither silently pass nor hard-crash
        print(f"HoneyPass guard error: {err}", file=sys.stderr)
        return EXIT_BLOCK if policy.get("fail_mode") == "closed" else EXIT_WARN
    if reasons:
        print("🛂 HoneyPass border guard BLOCKED this action:", file=sys.stderr)
        for reason in dict.fromkeys(reasons):
            print(f"  - {reason}", file=sys.stderr)
        print("If this is intended, ask the user to perform it manually.", file=sys.stderr)
        return EXIT_BLOCK
    return EXIT_ALLOW


if __name__ == "__main__":
    sys.exit(main())
