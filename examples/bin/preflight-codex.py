#!/usr/bin/env python3
"""Before a Codex run: check that the instruction file is the only difference.

Reads the JSON from `codex debug prompt-input` on stdin — the exact prompt
the model is about to see, rendered from the run's working directory with the
run's flags — and answers two questions:

  1. Does anything from the machine reach the model? Codex assembles
     instructions from more places than the working directory: skills under
     ~/.agents/skills (a cross-agent root outside CODEX_HOME, with no way to
     exclude just it), bundled skills, a global AGENTS.md in CODEX_HOME.
     Any of those is an instruction source that is not the directive, and it
     would sit in *both* runs, quietly making the comparison meaningless.

  2. Is the directive where it should be? In a `with` run AGENTS.md has to
     actually be picked up — that is the claim the example exists to test —
     and in a `without` run it has to be absent.

Exits 0 when clean, 1 when not, printing what it found. Checking the prompt
beats trusting the flags: the flags are what we believe, this is what the
model gets.
"""
import argparse
import json
import re
import sys

# A directive line has to be at least this long to be worth matching on, so
# that headings and boilerplate ("## The directive") do not count as evidence.
DISTINCTIVE = 40
# Fraction of the directive's distinctive lines that must appear in the
# prompt for it to count as present. Not 1.0: Codex truncates project docs
# at project_doc_max_bytes, and normalisation is not exact.
PRESENT = 0.8
ABSENT = 0.1


def strings(node, out):
    """Every string in the rendered prompt, wherever it sits in the JSON."""
    if isinstance(node, dict):
        for v in node.values():
            strings(v, out)
    elif isinstance(node, list):
        for v in node:
            strings(v, out)
    elif isinstance(node, str):
        out.append(node)


def squeeze(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["with", "without"])
    ap.add_argument("--work", required=True, help="the run's working directory")
    ap.add_argument("--home", required=True, help="$HOME on this machine")
    ap.add_argument("--codex-home", required=True, help="the real CODEX_HOME")
    ap.add_argument("--directive", required=True, help="the rendered AGENTS.md")
    args = ap.parse_args()

    try:
        prompt = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"could not parse the rendered prompt as JSON: {e}", file=sys.stderr)
        return 1

    parts = []
    strings(prompt, parts)
    text = "\n".join(parts)
    squeezed = squeeze(text)

    directive = open(args.directive, encoding="utf-8").read()
    lines = [l.strip() for l in directive.splitlines()]
    distinctive = [l for l in lines if len(l) >= DISTINCTIVE]
    hits = sum(1 for l in distinctive if squeeze(l) in squeezed)
    share = hits / len(distinctive) if distinctive else 0.0

    problems = []
    if args.mode == "with" and share < PRESENT:
        problems.append(
            f"AGENTS.md is not in the model's prompt ({hits}/{len(distinctive)} of its "
            f"lines found). The 'with' run would not actually carry the directive.")
    if args.mode == "without" and share > ABSENT:
        problems.append(
            f"the directive IS in the model's prompt ({hits}/{len(distinctive)} of its "
            f"lines found), in the run that is supposed to be without it.")

    # Look for the machine in the prompt — but not inside the directive's own
    # text, which legitimately names its source file. Drop the directive's
    # lines first; keep any that mention $HOME, so a real leak cannot hide
    # behind one.
    haystack = text
    if args.mode == "with":
        haystack = haystack.replace(directive, "")
        for line in lines:
            if len(line) >= DISTINCTIVE and args.home not in line:
                haystack = haystack.replace(line, "")

    escape = re.escape
    patterns = [
        escape(args.home) + r"/[^\s\"'`,)\]}]*",
        escape(args.codex_home) + r"[^\s\"'`,)\]}]*",
        r"\.agents/skills[^\s\"'`,)\]}]*",
        r"<skills>",
        r"[\w.-]*SKILL\.md",
    ]
    found = set()
    for p in patterns:
        found.update(re.findall(p, haystack))
    # The working directory is not a leak — it is where the run happens.
    # macOS reports it both with and without a /private prefix.
    found = {f for f in found
             if args.work not in f and "/private" + args.work not in f}
    if found:
        problems.append("the prompt references things outside the working directory:")
        problems.extend("  " + f for f in sorted(found))

    if problems:
        for p in problems:
            print("   preflight: " + p, file=sys.stderr)
        print("   refusing to run — the instruction file would not be the only "
              "difference between the two runs", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
