---
title: Skills in Claude Code
description: Quick reference for creating and organizing project or personal Skills when using the Claude Code CLI.
---

# Skills in Claude Code

Claude Code supports Skills, but the workflow differs slightly from the Anthropic API. Use this guide when adding Skills to this project so the configuration stays consistent and discoverable.

## Project vs Personal Skills

- **Project-wide Skills** live inside the repo and can be shared with collaborators: `.claude/skills/<skill-name>`.
- **Personal Skills** stay in your user config: `~/.claude/skills/<skill-name>`.
- The CLI automatically loads Skills that match the current operation; no manual invocation is needed once files exist.

## Creating a Skill

```bash
# project level
mkdir -p .claude/skills/my-skill-name

# personal level
mkdir -p ~/.claude/skills/my-skill-name
```

Rules:
- `name`: lowercase letters, numbers, hyphens only (≤64 chars).
- Add supporting assets (scripts, templates, docs) inside the skill folder as needed.

## Required SKILL.md

Every skill folder must contain `SKILL.md` with a short header block followed by detailed guidance:

```markdown
---
name: my-skill-name
description: Brief explanation of what the skill does and when Claude should invoke it (≤1024 chars)
---

# My Skill Name

## Instructions
Step-by-step directions for Claude when applying this skill.

## Examples
Concrete, high-signal examples that show ideal usage.
```

Tips:
- Keep instructions actionable; note any dependencies or expected files.
- Examples should show both the trigger scenario and the desired response.

## Suggested Project Layout

```
.claude/
└── skills/
    └── your-skill-name/
        ├── SKILL.md         # Required instructions + metadata
        ├── scripts/         # Optional helper scripts
        └── templates/       # Optional prompt/code templates
```

If you mirror docs locally for reference, place them under `_context/documentation/anthropic/claude-code/` using descriptive filenames (e.g., `skills.md`—this file).
