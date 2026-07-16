---
name: obsidian-vault
description: Deprecated. Historical workflow for managing notes in a local Obsidian vault; use Brain instead.
---

<!-- Derived from:
https://github.com/mattpocock/skills/blob/main/skills/personal/obsidian-vault/SKILL.md
Customized with a local vault path.
-->

# Obsidian Vault

> **Deprecated:** The configured vault was migrated to Brain on 2026-07-15. This skill remains only as a historical reference; use the `brain` skill for persistent knowledge.

## Vault location

`$HOME/ws/repos/obsidian-vault/`

Mostly flat at root level.

## Naming conventions

- **Index notes**: aggregate related topics (e.g., `Ralph Wiggum Index.md`, `Skills Index.md`, `RAG Index.md`)
- **Title case** for all note names
- No folders for organization - use links and index notes instead

## Linking

- Use Obsidian `[[wikilinks]]` syntax: `[[Note Title]]`
- Notes link to dependencies/related notes at the bottom
- Index notes are just lists of `[[wikilinks]]`

## Workflows

### Search for notes

```bash
# Search by filename
find "$HOME/ws/repos/obsidian-vault/" -name "*.md" | grep -i "keyword"

# Search by content
grep -rl "keyword" "$HOME/ws/repos/obsidian-vault/" --include="*.md"
```

Or use Grep/Glob tools directly on the vault path.

### Create a new note

1. Use **Title Case** for filename
2. Write content as a unit of learning (per vault rules)
3. Add `[[wikilinks]]` to related notes at the bottom
4. If part of a numbered sequence, use the hierarchical numbering scheme

### Find related notes

Search for `[[Note Title]]` across the vault to find backlinks:

```bash
grep -rl "\\[\\[Note Title\\]\\]" "$HOME/ws/repos/obsidian-vault/"
```

### Find index notes

```bash
find "$HOME/ws/repos/obsidian-vault/" -name "*Index*"
```
