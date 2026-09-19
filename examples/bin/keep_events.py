#!/usr/bin/env python3
"""Filter for the raw stream-json kept under raw/.

Drops exactly two event types, both of which carry no transcript content:
  stream_event       token-level partial deltas; every one of them is repeated
                     in full in the following `assistant` event
  system/commands_changed
                     the list of slash commands installed on the machine the
                     run happened on — environment noise, not the run
Every other line passes through byte-for-byte, malformed lines included.

It also prints a one-line progress note per event to stderr, so a run that
takes a minute does not look like a hang.
"""
import json
import sys

# `keep_events.py --failed < raw.jsonl` exits 0 if the run produced no real
# answer (the result event is missing or flagged is_error), 1 otherwise.
if len(sys.argv) > 1 and sys.argv[1] == "--failed":
    result = None
    for line in sys.stdin:
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "result":
            result = e
    sys.exit(0 if result is None or result.get("is_error") else 1)


def note(msg: str) -> None:
    sys.stderr.write(f"   {msg}\n")
    sys.stderr.flush()


for line in sys.stdin:
    try:
        e = json.loads(line)
    except json.JSONDecodeError:
        sys.stdout.write(line)
        sys.stdout.flush()
        continue
    t = e.get("type")
    if t == "stream_event":
        continue
    if t == "system" and e.get("subtype") == "commands_changed":
        continue
    if t == "system" and e.get("subtype") == "init":
        note(f"model {e.get('model')} — thinking…")
    elif t == "assistant":
        for b in e.get("message", {}).get("content", []):
            if b.get("type") == "tool_use":
                note(f"tool: {b.get('name')}")
            elif b.get("type") == "text" and b.get("text", "").strip():
                note("agent replied (%d chars)" % len(b["text"]))
    elif t == "result":
        note(f"result: {e.get('subtype')} after {e.get('num_turns')} turn(s), {e.get('duration_ms', 0) // 1000}s")
    sys.stdout.write(line)
    sys.stdout.flush()
