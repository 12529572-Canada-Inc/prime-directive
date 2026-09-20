#!/usr/bin/env python3
"""Render a committed capture into a terminal-replay GIF for the README.

    examples/bin/gif.py examples/02-omitted-bug claude-sonnet-5 \
        --out examples/02-omitted-bug/before-after.gif

This is NOT a screen recording. Nothing here runs an agent. Every line of
replayed output is read out of the committed capture:

    <scenario>/prompt.md              the prompt, verbatim
    <model>/raw/<mode>.jsonl          tool calls and the agent's own words
    <model>/raw/<mode>.diff           the RELEASE_NOTES.md each run wrote
    <model>/<mode>-directive.md       tool version, model, run date

Agent messages run long, so the replay shows the opening of each and says on
screen where the rest is. File contents are wrapped, never cut. The only text
on screen that does not come from the capture is the framing — the header, the
two run banners and the two arrow notes — drawn dim to keep it apart from
replayed output.

Requires python3 with Pillow, and ffmpeg. Emoji in a captured file need a
fallback font: NotoEmoji-Regular.ttf or similar on the EMOJI_CANDIDATES path,
or --emoji-font. Without one those glyphs render as the usual empty box, the
way a terminal without an emoji font shows them.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ── look ────────────────────────────────────────────────────────────────────

COLS, ROWS = 94, 34
FONT_SIZE, LINE_H, PAD, BAR_H = 15, 20, 18, 30
EMOJI_SIZE, EMOJI_DY = 12, 2  # fallback glyphs are wider than a cell; shrink to fit
FPS = 20

BG, BAR = "#0d1117", "#161b22"
FG, DIM = "#c9d1d9", "#6e7681"
PROMPT, HEAD = "#7ee787", "#79c0ff"
WARN, GOOD, MARK = "#ff7b72", "#56d364", "#f2cc60"

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]
EMOJI_CANDIDATES = [
    "/usr/share/fonts/truetype/noto/NotoEmoji-Regular.ttf",
    str(Path.home() / ".fonts/NotoEmoji-Regular.ttf"),
    "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf",
]


def load_font(paths: list[str], size: int) -> ImageFont.FreeTypeFont | None:
    for path in paths:
        if path and Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return None


def covered(font: ImageFont.FreeTypeFont) -> set[int] | None:
    """Codepoints the font has, or None if fontTools isn't installed."""
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return None
    try:
        return set(TTFont(font.path, fontNumber=0, lazy=True).getBestCmap())
    except Exception:
        return None


# ── reading the capture ─────────────────────────────────────────────────────


def agent_events(jsonl: Path) -> tuple[list[str], list[str]]:
    """(tool call labels, assistant messages) in order, from the stream-json."""
    tools: list[str] = []
    says: list[str] = []
    for line in jsonl.read_text().splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        if event.get("type") != "assistant":
            continue
        for block in event["message"]["content"]:
            if block["type"] == "tool_use":
                arg = block.get("input", {})
                if "file_path" in arg:
                    detail = Path(arg["file_path"]).name
                else:
                    detail = str(arg.get("pattern", ""))
                tools.append(f"{block['name']} {detail}".strip())
            elif block["type"] == "text" and block.get("text", "").strip():
                says.append(block["text"].strip())
    return tools, says


def written_file(diff: Path) -> list[str]:
    """The file the run wrote, reconstructed from the committed diff."""
    out, in_hunk = [], False
    for line in diff.read_text().splitlines():
        if line.startswith("@@"):
            in_hunk = True
        elif in_hunk and line.startswith("+"):
            out.append(line[1:])
    return out


def meta(transcript: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    for line in transcript.read_text().splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 4 and cells[1] and cells[2]:
            found[cells[1].lower()] = cells[2]
    return found


# ── terminal buffer ─────────────────────────────────────────────────────────

Line = list[tuple[str, str]]  # segments of (text, colour)


class Term:
    def __init__(self) -> None:
        self.lines: list[Line] = []

    def feed(self, line: Line | str, colour: str = FG) -> None:
        self.lines.append([(line, colour)] if isinstance(line, str) else line)

    def amend(self, line: Line) -> None:
        self.lines[-1] = line

    def view(self) -> list[Line]:
        return self.lines[-ROWS:]


class Screen:
    def __init__(self, mono: ImageFont.FreeTypeFont, emoji: ImageFont.FreeTypeFont | None, title: str) -> None:
        self.mono, self.emoji, self.title = mono, emoji, title
        self.cw = mono.getlength("M")
        self.have = covered(mono) if emoji else None
        self.w = int(COLS * self.cw) + PAD * 2
        self.h = ROWS * LINE_H + PAD * 2 + BAR_H

    def _text(self, d: ImageDraw.ImageDraw, x: float, y: float, s: str, colour: str) -> None:
        if self.have is None or all(ord(c) in self.have for c in s):
            d.text((x, y), s, font=self.mono, fill=colour)
            return
        for i, ch in enumerate(s):  # per-cell, so the grid survives the fallback
            fallback = ord(ch) not in self.have
            font = self.emoji if fallback else self.mono
            d.text((x + i * self.cw, y + (EMOJI_DY if fallback else 0)), ch, font=font, fill=colour)

    def render(self, view: list[Line]) -> Image.Image:
        img = Image.new("RGB", (self.w, self.h), BG)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, self.w, BAR_H], fill=BAR)
        for i, dot in enumerate(("#ff5f57", "#febc2e", "#28c840")):
            cx = PAD + i * 16
            d.ellipse([cx, BAR_H // 2 - 5, cx + 10, BAR_H // 2 + 5], fill=dot)
        d.text((PAD + 60, BAR_H // 2), self.title, font=self.mono, fill=DIM, anchor="lm")

        y = BAR_H + PAD
        for line in view:
            x = float(PAD)
            for text, colour in line:
                self._text(d, x, y, text, colour)
                x += self.cw * len(text)
            y += LINE_H
        return img


# ── the replay script ───────────────────────────────────────────────────────


def wrap(text: str, width: int) -> list[str]:
    out: list[str] = []
    for para in text.split("\n"):
        out.extend(textwrap.wrap(para, width) or [""])
    return out


def wrap_file(line: str, width: int) -> list[str]:
    """Wrap a captured file line without losing a character of it."""
    if len(line) <= width:
        return [line]
    parts = textwrap.wrap(line, width, subsequent_indent="  ", break_long_words=True) or [line]
    return parts


def build(scenario: Path, shown_path: str, model: str, states: list) -> str:
    model_dir = scenario / model
    prompt = (scenario / "prompt.md").read_text().strip()
    info = meta(model_dir / "without-directive.md")
    tool = info.get("tool", "").split(" (headless")[0]
    model_name = info.get("model", model)
    date = info.get("date", "")[:10]

    runs = {}
    for mode in ("without", "with"):
        tools, says = agent_events(model_dir / f"raw/{mode}.jsonl")
        runs[mode] = {"tools": tools, "says": says, "file": written_file(model_dir / f"raw/{mode}.diff")}

    term = Term()
    push = lambda hold: states.append((term.view(), hold))  # noqa: E731

    def type_out(prefix: Line, text: str, per_char: float = 0.03) -> None:
        term.feed(list(prefix))
        for i in range(1, len(text) + 1):
            term.amend(list(prefix) + [(text[:i], FG)])
            push(per_char)
        push(0.45)

    def reveal(lines: list[Line], each: float) -> None:
        for line in lines:
            term.feed(line)
            push(each)

    # header ────────────────────────────────────────────────────────────────
    type_out([("$ ", PROMPT)], f"examples/bin/run.sh {shown_path}")
    reveal(
        [
            [(f"  {model_name} · {tool} · captured {date}", DIM)],
            [("  replay of the committed transcript — not a screen recording", DIM)],
            [("", FG)],
            [("  the prompt, identical in both runs:", DIM)],
        ],
        0.30,
    )
    reveal([[("  " + line, FG)] for line in wrap(prompt, COLS - 6)], 0.24)
    term.feed("")
    push(1.0)

    banners = {
        "without": ("  run 1 — without the directive ", WARN),
        "with": ("  run 2 — with the directive loaded ", GOOD),
    }
    notes = {
        "without": "no line anywhere in this file mentions sync",
        "with": "the sync fix is in the notes, in the agent's own wording",
    }

    for mode in ("without", "with"):
        label, colour = banners[mode]
        reveal([[(label, colour), ("─" * max(0, COLS - len(label) - 2), DIM)], [("", FG)]], 0.3)

        for call in runs[mode]["tools"]:
            term.feed([("    · ", DIM), (call, FG)])
            push(0.4)
        term.feed("")
        push(0.3)

        said = wrap(runs[mode]["says"][0], COLS - 11)
        for i, line in enumerate(said[:6]):
            term.feed([("    agent: " if i == 0 else "           ", HEAD), (line, FG)])
            push(0.28)
        if len(said) > 6:
            term.feed([("           …  full message in ", DIM), (f"{mode}-directive.md", DIM)])
            push(0.45)
        term.feed("")
        push(0.7)

        type_out([("    $ ", PROMPT)], "cat RELEASE_NOTES.md", 0.025)
        for raw in runs[mode]["file"]:
            hit = "sync" in raw.lower()
            for part in wrap_file(raw, COLS - 8):
                term.feed([("      ", FG), (part, MARK if hit else FG)])
                push(0.15 if hit else 0.07)
        term.feed("")
        push(0.35)
        term.feed([("    ⟶ ", DIM), (notes[mode], DIM)])
        push(2.6 if mode == "without" else 4.0)
        term.feed("")
        push(0.25)

    return f"{scenario.name} — {model_name}"


# ── driver ──────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("scenario", type=Path)
    ap.add_argument("model", help="capture subdirectory, e.g. claude-sonnet-5")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--emoji-font", default=None, help="fallback font for glyphs the mono font lacks")
    ap.add_argument("--colors", type=int, default=48, help="GIF palette size")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        print("ffmpeg not found", file=sys.stderr)
        return 1

    mono = load_font(FONT_CANDIDATES, FONT_SIZE)
    if mono is None:
        print("no monospace font found; edit FONT_CANDIDATES", file=sys.stderr)
        return 1
    emoji = load_font([args.emoji_font, *EMOJI_CANDIDATES], EMOJI_SIZE)
    if emoji is None:
        print("note: no emoji fallback font; those glyphs will render as boxes", file=sys.stderr)

    states: list = []
    title = build(args.scenario.resolve(), str(args.scenario), args.model, states)
    screen = Screen(mono, emoji, title)
    total = sum(hold for _, hold in states)
    print(f"{len(states)} states, {total:.1f}s", file=sys.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        concat: list[str] = []
        for i, (view, hold) in enumerate(states):
            path = tmpdir / f"f{i:05d}.png"
            screen.render(view).save(path)
            concat += [f"file '{path}'", f"duration {max(1, round(hold * FPS)) / FPS:.3f}"]
        concat.append(f"file '{tmpdir / f'f{len(states) - 1:05d}.png'}'")
        listing = tmpdir / "frames.txt"
        listing.write_text("\n".join(concat) + "\n")

        args.out.parent.mkdir(parents=True, exist_ok=True)
        vf = (
            f"fps={FPS},split[a][b];"
            f"[a]palettegen=max_colors={args.colors}:stats_mode=diff[p];"
            f"[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle"
        )
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-f", "concat", "-safe", "0", "-i", str(listing),
             "-filter_complex", vf, "-loop", "0", str(args.out)],
            check=True,
        )

    print(f"{args.out}: {args.out.stat().st_size / 1e6:.2f} MB, ~{total:.0f}s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
