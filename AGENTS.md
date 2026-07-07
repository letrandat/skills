# Agent Guidelines

Skills in this repository are organized into bucket folders under `skills/`:

- `engineering/` — daily code work (promoted)
- `productivity/` — daily non-code workflow tools (promoted)
- `misc/` — kept around but rarely used, not promoted
- `personal/` — tied to my own setup, not promoted
- `in-progress/` — drafts not yet ready to ship
- `deprecated/` — no longer used

## Rules for Adding/Modifying Skills

1. **Promotion Rules**:
   - Every skill in `engineering/` or `productivity/` (the **promoted** buckets) must have a reference in the top-level `README.md` and an entry in `.claude-plugin/plugin.json` (for Claude Code compatibility).
   - Skills in `misc/`, `personal/`, `in-progress/`, and `deprecated/` must not appear in the top-level catalog or `.claude-plugin/plugin.json`.

2. **Bucket-Level Catalogs**:
   - Each bucket folder has a `README.md` that lists every skill in that bucket with a one-line description, with the skill name linked to its `SKILL.md`.
   - Promoted buckets (`engineering/`, `productivity/`) group entries into **User-invoked** and **Model-invoked**.
   - Non-promoted buckets (`misc/`, `personal/`) use a flat bulleted list.

3. **Links**:
   - Always link skill names directly to their respective `SKILL.md` files.
