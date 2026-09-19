#!/usr/bin/env python3
"""Filter for the raw stream-json kept under raw/.

Drops exactly two event types, both of which carry no transcript content:
  stream_event       token-level partial deltas; every one of them is repeated
                     in full in the following `assistant` event
  system/commands_changed
                     the list of slash commands installed on the machine the
                     run happened on — environment noise, not the run
Every other line passes through byte-for-byte, malformed lines included.
"""
import json
import sys

for line in sys.stdin:
    try:
        e = json.loads(line)
    except json.JSONDecodeError:
        sys.stdout.write(line)
        continue
    if e.get("type") == "stream_event":
        continue
    if e.get("type") == "system" and e.get("subtype") == "commands_changed":
        continue
    sys.stdout.write(line)
