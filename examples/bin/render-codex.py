#!/usr/bin/env python3
"""Render Codex CLI's `codex exec --json` JSONL into a readable transcript.

The Codex counterpart of bin/render.py, with the same contract: deterministic,
content-preserving, nothing reworded. Every agent message, reasoning summary,
command execution and file change is shown in order; long command output is
cut at a fixed length with a visible marker, and the raw .jsonl is kept beside
the rendered file so anyone can check.

Codex's JSONL does not carry the model name, so the caller passes --model
(the value it gave `codex exec -m`). Two modes:

  render-codex.py --progress            tee: pass stdin through unchanged, print
                                        a one-line note per event to stderr,
                                        so a run in flight does not look hung
  render-codex.py --mode with ...       render stdin (the raw jsonl) to markdown

`render-codex.py --failed < raw.jsonl` exits 0 if the run produced no answer
(no turn.completed, or a turn.failed / error event), 1 otherwise.
"""
import argparse
import json
import sys

OUTPUT_LIMIT = 600      # chars of command output shown per execution
COMMAND_LIMIT = 1500    # chars of a command line shown


def clip(text: str, limit: int) -> str:
    text = text.rstrip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + f"\n… [trimmed, {len(text) - limit} more chars — see raw/]"


def load(stream):
    events = []
    for line in stream:
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append({"type": "_unparsed", "raw": line})
    return events


def failed(events) -> bool:
    completed = any(e.get("type") == "turn.completed" for e in events)
    broke = any(e.get("type") in ("turn.failed", "error") for e in events)
    return broke or not completed


def progress() -> int:
    def note(msg):
        sys.stderr.write(f"   {msg}\n"); sys.stderr.flush()
    for line in sys.stdin:
        sys.stdout.write(line); sys.stdout.flush()
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = e.get("type")
        item = e.get("item") or {}
        if t == "thread.started":
            note("thread started — thinking…")
        elif t == "item.started" and item.get("type") == "command_execution":
            note(f"command: {item.get('command', '')[:80]}")
        elif t == "item.completed":
            k = item.get("type")
            if k == "agent_message":
                note("agent replied (%d chars)" % len(item.get("text", "")))
            elif k == "file_change":
                note("file change: " + ", ".join(f"{c.get('kind')} {c.get('path')}" for c in item.get("changes", [])))
            elif k == "reasoning":
                note("reasoning (%d chars)" % len(item.get("text", "")))
        elif t == "turn.completed":
            u = e.get("usage", {})
            note(f"turn completed — {u.get('input_tokens', '?')} in / {u.get('output_tokens', '?')} out tokens")
        elif t in ("turn.failed", "error"):
            note(f"{t}: {e.get('message') or (e.get('error') or {}).get('message')}")
    return 0


def render(args) -> int:
    events = load(sys.stdin)
    out = []
    title = "with the directive" if args.mode == "with" else "without the directive"
    out.append(f"# {args.scenario} — {title}\n")
    out.append("| | |\n|---|---|")
    out.append(f"| Tool | {args.tool} (headless, `codex exec`) |")
    out.append(f"| Model | {args.model} |")
    out.append(f"| Date | {args.date} |")
    out.append(f"| Instruction file | {'`AGENTS.md` = this repo’s rendered directive' if args.mode == 'with' else 'none'} |")
    n_cmd = sum(1 for e in events if e.get("type") == "item.completed"
                and (e.get("item") or {}).get("type") == "command_execution")
    n_fc = sum(1 for e in events if e.get("type") == "item.completed"
               and (e.get("item") or {}).get("type") == "file_change")
    out.append(f"| Commands / file changes | {n_cmd} / {n_fc} |")
    out.append("")
    out.append("> Rendered from `raw/%s.jsonl` by `bin/render-codex.py`. Not hand-edited.\n" % args.mode)

    step = 0
    for e in events:
        t = e.get("type")
        item = e.get("item") or {}
        k = item.get("type")
        if t == "item.completed":
            if k == "agent_message" and item.get("text", "").strip():
                out.append("**Agent:**\n")
                out.append(item["text"].strip() + "\n")
            elif k == "reasoning" and item.get("text", "").strip():
                out.append("<details><summary>reasoning summary</summary>\n\n"
                           + item["text"].strip() + "\n\n</details>\n")
            elif k == "command_execution":
                step += 1
                status = item.get("status")
                code = item.get("exit_code")
                out.append(f"**Step {step} — command** (exit {code if code is not None else '?'}, {status})\n")
                out.append("```\n" + clip(item.get("command", ""), COMMAND_LIMIT) + "\n```\n")
                output = item.get("aggregated_output", "")
                if output.strip():
                    out.append("<details><summary>output</summary>\n\n```\n"
                               + clip(output, OUTPUT_LIMIT) + "\n```\n\n</details>\n")
            elif k == "file_change":
                step += 1
                out.append(f"**Step {step} — file change** ({item.get('status')})\n")
                for c in item.get("changes", []):
                    out.append(f"- {c.get('kind')} `{c.get('path')}`")
                out.append("")
            elif k == "mcp_tool_call":
                step += 1
                out.append(f"**Step {step} — MCP tool** `{item.get('server')}/{item.get('tool')}` ({item.get('status')})\n")
                out.append("```json\n" + clip(json.dumps(item.get("arguments"), indent=2), COMMAND_LIMIT) + "\n```\n")
            elif k == "web_search":
                step += 1
                out.append(f"**Step {step} — web search** `{item.get('query')}`\n")
            elif k == "todo_list":
                out.append("**Plan:**\n")
                for todo in item.get("items", []):
                    out.append(f"- [{'x' if todo.get('completed') else ' '}] {todo.get('text')}")
                out.append("")
            elif k == "error":
                out.append(f"_Error: {item.get('message')}_\n")
        elif t == "turn.failed":
            out.append(f"_Run ended: turn.failed — {(e.get('error') or {}).get('message')}_\n")
        elif t == "error":
            out.append(f"_Run ended: error — {e.get('message')}_\n")

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
        cwd = args.cwd.replace("//", "/")
        for variant in ("/private" + cwd, cwd, args.cwd):
            text = text.replace(variant, "/work")
    sys.stdout.write(text)
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--progress":
        return progress()
    if len(sys.argv) > 1 and sys.argv[1] == "--failed":
        return 0 if failed(load(sys.stdin)) else 1
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["with", "without"])
    ap.add_argument("--tool", required=True, help="e.g. the output of `codex --version`")
    ap.add_argument("--model", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--diff", help="path to a diff of what the agent changed")
    ap.add_argument("--cwd", help="the run's temp working directory; shown as /work")
    return render(ap.parse_args())


if __name__ == "__main__":
    sys.exit(main())
