# Dat's Skills

My personal agent skills that I use to guide AI coding agents (Antigravity, Codex, Claude Code, and others) to follow professional standards and automate workflows.

These skills are designed to be small, easy to adapt, and composable.

## Quickstart

1. Run the skills installer:

```bash
npx skills@latest add letrandat/skills
```

2. Select the skills you want, and which coding agents you want to install them on.

## Catalog

### Engineering Skills (Promoted)
These are daily code-work skills. You can view the full list in the [skills/engineering/](./skills/engineering/README.md) directory.

- [sharpen-prompt](./skills/engineering/sharpen-prompt/SKILL.md) — Turn a rough coding request into a short poteto-mode prompt with a goal, a guard, and a done-check.

### Productivity Skills (Promoted)
These are daily non-code workflow tools to improve productivity. You can view the full list in the [skills/productivity/](./skills/productivity/README.md) directory.

- [brain](./skills/productivity/brain/SKILL.md) — Record, recall, revise, connect, and review a persistent OKF v0.1 second brain.
- [eli5](./skills/productivity/eli5/SKILL.md) — Explain like I am 5.
- [say-it](./skills/productivity/say-it/SKILL.md) — One speakable cue when a dictated word was their pronunciation and they will say it themselves.

## Prompts

Portable, zero-dependency prompts for off-machine use across any agent harness. See the [prompts/](./prompts/README.md) directory for details.

- [system-diagram-grill](./prompts/system-diagram-grill.md) — Survey and grill complex subsystem architecture, dataflow, and boundaries into diagrams.
- [pr-flow-diagram-grill](./prompts/pr-flow-diagram-grill.md) — Group PR code changes into functional flows, propose diagrams, and walk the code.
- [ticket-solution-diagram-grill](./prompts/ticket-solution-diagram-grill.md) — Dissect an issue into paired As-Is failure mode vs To-Be invariant fix before writing code.

