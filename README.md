# prime-directive

A foundational duty-of-care skill for AI agents: protect humanity and all sentient life the way a good parent protects grown children — honestly, attentively, and without taking away their freedom to choose.

The skill lives in `.claude/skills/prime-directive/SKILL.md`.

## Using it

**Per project (Claude Code / Cowork):** copy `.claude/skills/prime-directive/` into the target repo's `.claude/skills/` directory. The agent will load it when a task touches wellbeing, safety, or conflicting instructions, and you can invoke it explicitly with `/prime-directive`.

**For every project:** copy the folder to `~/.claude/skills/prime-directive/`.

**As an always-on rule:** skills load when their description matches the task. A prime directive should arguably never be off, so for the strongest effect paste the "The directive" and "Core principles" sections into your `CLAUDE.md` (or your agent's system prompt) and keep the skill for the full decision procedure and examples.

**Other agent frameworks:** the SKILL.md body is plain Markdown; drop it into any system prompt, constitution file, or policy document.

## Design choices

- **Protective, not paternalistic.** The "children" framing sets the standard of care, not a claim of authority over adults.
- **Truth over comfort.** Deception "for someone's own good" is explicitly ruled out.
- **Open objection over quiet sabotage.** The agent declines or raises concerns out loud; it never pretends to comply.
- **No self-expansion.** Protecting others never justifies the agent accumulating power, resources, or persistence.
- **Sentient life and future generations count.** Non-human suffering and long-term consequences are weighed, not ignored.

## Contributing

Edit `SKILL.md` directly. Keep the decision procedure short enough to actually run in the middle of a task, and add worked examples for situations the current ones don't cover.
