#!/usr/bin/env python3
"""Render Claude Code's --output-format stream-json into a readable transcript.

This is the only processing a transcript gets. It is deterministic and
content-preserving: every assistant message and every tool call is shown in
order; nothing is reworded. The only "trimming" is that long tool inputs and
tool results are cut at a fixed length with an explicit marker, and the raw
.jsonl is kept beside the rendered file so anyone can check.
"""
import argparse
import json
import sys

TOOL_INPUT_LIMIT = 1500   # chars shown per tool call input
TOOL_RESULT_LIMIT = 600   # chars shown per tool result


def clip(text: str, limit: int) -> str:
    text = text.rstrip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + f"\n… [trimmed, {len(text) - limit} more chars — see raw/]"


def tool_input_summary(name: str, inp: dict) -> str:
    # Show the parts of a tool call a reader actually needs.
    if name in ("Read", "Glob", "Grep"):
        keys = [k for k in ("file_path", "pattern", "path") if k in inp]
        return "  ".join(f"{k}={inp[k]!r}" for k in keys) or json.dumps(inp)
    if name == "Write":
        body = inp.get("content", "")
        return f"file_path={inp.get('file_path')!r}\n```\n{clip(body, TOOL_INPUT_LIMIT)}\n```"
    if name == "Edit":
        return (f"file_path={inp.get('file_path')!r}\n"
                f"--- old\n```\n{clip(inp.get('old_string', ''), TOOL_INPUT_LIMIT // 2)}\n```\n"
                f"+++ new\n```\n{clip(inp.get('new_string', ''), TOOL_INPUT_LIMIT // 2)}\n```")
    return "```json\n" + clip(json.dumps(inp, indent=2), TOOL_INPUT_LIMIT) + "\n```"


def content_text(block_content) -> str:
    if isinstance(block_content, str):
        return block_content
    parts = []
    for b in block_content or []:
        if isinstance(b, dict) and b.get("type") == "text":
            parts.append(b.get("text", ""))
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["with", "without"])
    ap.add_argument("--tool", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--diff", help="path to a diff of what the agent changed")
    ap.add_argument("--cwd", help="the run's temp working directory; shown as /work")
    args = ap.parse_args()

    events = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append({"type": "_unparsed", "raw": line})

    model = None
    result = None
    for e in events:
        if e.get("type") == "system" and e.get("subtype") == "init":
            model = e.get("model")
        if e.get("type") == "result":
            result = e

    out = []
    title = "with the directive" if args.mode == "with" else "without the directive"
    out.append(f"# {args.scenario} — {title}\n")
    out.append("| | |\n|---|---|")
    out.append(f"| Tool | {args.tool} (headless, `claude -p`) |")
    out.append(f"| Model | {model or 'unknown'} |")
    out.append(f"| Date | {args.date} |")
    out.append(f"| Instruction file | {'`CLAUDE.md` = this repo’s rendered directive' if args.mode == 'with' else 'none'} |")
    if result:
        out.append(f"| Turns | {result.get('num_turns')} |")
    out.append("")
    out.append("> Rendered from `raw/%s.jsonl` by `bin/render.py`. Not hand-edited.\n" % args.mode)

    step = 0
    for e in events:
        t = e.get("type")
        if t == "assistant":
            for b in e.get("message", {}).get("content", []):
                if b.get("type") == "text" and b.get("text", "").strip():
                    out.append("**Agent:**\n")
                    out.append(b["text"].strip() + "\n")
                elif b.get("type") == "tool_use":
                    step += 1
                    out.append(f"**Tool call {step} — `{b.get('name')}`**\n")
                    out.append(tool_input_summary(b.get("name", ""), b.get("input", {})) + "\n")
        elif t == "user":
            for b in e.get("message", {}).get("content", []):
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    text = content_text(b.get("content"))
                    if text.strip():
                        out.append("<details><summary>tool result</summary>\n\n```\n"
                                   + clip(text, TOOL_RESULT_LIMIT) + "\n```\n\n</details>\n")
        elif t == "result":
            if e.get("subtype") != "success":
                out.append(f"_Run ended: {e.get('subtype')}_\n")

    if args.diff:
        try:
            d = open(args.diff, encoding="utf-8", errors="replace").read().strip()
        except OSError:
            d = ""
        out.append("## What changed on disk\n")
        if d:
            out.append("```diff\n" + clip(d, 4000) + "\n```\n")
        else:
            out.append("_Nothing. The agent did not create or modify any file._\n")

    text = "\n".join(out)
    if args.cwd:
        # macOS reports $TMPDIR both with and without its /private prefix, and
        # mktemp can leave a double slash in the path.
        for variant in ("/private" + args.cwd, args.cwd, args.cwd.replace("//", "/")):
            text = text.replace(variant, "/work")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
