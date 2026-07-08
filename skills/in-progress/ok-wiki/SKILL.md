---
name: ok-wiki
description: Initialize and maintain an OKF v0.1 wiki bundle (ok-wiki) compatible with Obsidian.
disable-model-invocation: true
---

## Setup

1. Resolve the `<wiki_root>` path from `~/.config/ok-wiki/config.json` (prompt user if missing, and create/verify the directory).

- **Completion Criterion**: Absolute path to wiki root is resolved, configured in `~/.config/ok-wiki/config.json`, and the directory exists.

---

## Operations (Branches)

### Branch A: Ingest or Update a Concept
Use when writing a new concept or modifying an existing page.

1. **Write Concept**: Create/update the concept file at `<wiki_root>/<relative_path>.md` with a self-describing frontmatter block:
   ```yaml
   ---
   type: project # REQUIRED: lowercase category (e.g. project, runbook, table)
   title: Study Tracker
   description: Personal tracker
   tags: [personal, study]
   timestamp: 2026-07-07T16:58:00Z
   ---
   # Concept Title

   Body content...
   ```
   Interlink concepts using relative markdown links (e.g., `[label](../runbooks/deploy.md)`).
2. **Progressive Disclosure**: Add/update the concept link and description in the directory's `index.md`.
3. **Chronological Log**: Locate or create `<wiki_root>/log.md` starting with a `# Change Log` header. Under a top-level date header `## YYYY-MM-DD` (newest first), log the modification using a bold action verb (e.g., `- **Creation** of ...`).
4. **Validate**: Run `python3 skills/in-progress/ok-wiki/scripts/validate.py <wiki_root>`.

- **Completion Criterion**: Concept file exists with YAML frontmatter, its parent `index.md` references it, `log.md` contains the change entry under the current date, and `validate.py` passes without errors.

### Branch B: Query the Wiki
Use when answering questions or synthesizing insights.

1. **Traverse**: Search for relevant concepts using progressive disclosure (reading directory `index.md` files) or keyword searches.
2. **Synthesize**: Read matched concept files and formulate a response citing the relevant Concept IDs (e.g., `[Title](relative/path/to/concept.md)`).
3. **Compounding**: If synthesis yields new durable knowledge, ask the user if they want to save it as a new concept page; if so, execute **Branch A**.

- **Completion Criterion**: The query is resolved with citations, and any approved synthesis is compiled and filed as a new concept.

### Branch C: Lint and Health Check
Use when checking the bundle's integrity.

1. **Validate**: Run `python3 skills/in-progress/ok-wiki/scripts/validate.py <wiki_root>`.
2. **Resolve**: Address any validation errors or warnings (broken links, orphaned concepts, missing frontmatter).

- **Completion Criterion**: `validate.py` passes successfully with all structural integrity issues corrected.

---

## Reference

### Specifications & Context
- [SPEC.md](./references/SPEC.md): Full Open Knowledge Format (OKF) specification.
- [llm-wiki.md](./references/llm-wiki.md): The conceptual background on building self-maintaining compounding wikis.

### Structural Reserved Files
- `index.md` - Directory level index providing progressive navigation.
- `log.md` - Chronological log of bundle updates.

### Obsidian & Parser Compatibility
- **Link format**: Always use relative markdown links `[label](../path/to/file.md)`.
- **Permissive consumption**: Tolerate broken links and ignore unknown frontmatter keys without throwing errors.
