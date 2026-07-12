---
name: obsidian-vault
description: Search, create, and manage notes in the Obsidian vault with wikilinks and index notes. Use when user wants to find, create, or organize notes in Obsidian.
---

<!-- Derived from:
https://github.com/mattpocock/skills/blob/main/skills/personal/obsidian-vault/SKILL.md
Customized with a local vault path.
-->

# Obsidian Vault

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
