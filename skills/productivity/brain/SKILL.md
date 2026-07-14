---
name: brain
description: Manage a persistent second brain. Use only when the user explicitly invokes Brain to record, recall, revise, connect, or review durable knowledge.
disable-model-invocation: true
---

## How to Talk to Brain

Invoke Brain explicitly, then describe the outcome naturally. The operation names below are a guide, not required command syntax.

| Operation | Purpose | Natural requests |
| --- | --- | --- |
| **Record** | Incorporate new durable knowledge. | “Remember this.” “Record what we learned today.” “Save this knowledge.” |
| **Recall** | Retrieve and synthesize stored knowledge without changing Brain. | “Tell me about deployment.” “What do we know about authentication?” |
| **Revise** | Intentionally correct, restructure, or replace existing knowledge. | “Correct the deployment concept.” “Fix what we know about rollback.” |
| **Connect** | Create meaningful relationships between concepts. | “Connect these ideas.” “How are deployment failures and rollback related?” |
| **Review / Reflect** | Inspect knowledge for conflicting facts, gaps, staleness, weak support, and structural problems. | “Review Brain’s health.” “Find conflicting facts.” “What are we missing?” |

If the right operation is unclear, use **Record** or say “Remember this.” Brain inspects existing concepts and decides whether to create a concept or incorporate the knowledge into an existing one.

### Read-Only and Changing Operations

- **Recall**, external research, and **Review / Reflect** are read-only by default.
- Changing Brain requires an explicit action such as record, remember, revise, correct, fix, repair, or connect.
- Operations may be combined. “Review Brain, then fix safe structural issues” means inspect first, apply only the authorized deterministic repairs, and report both findings and changes.
- Authorization to fix structural issues never authorizes changing substantive knowledge. Brain asks before resolving ambiguous or conflicting claims unless the user supplied the evidence and explicitly requested the correction.

### Examples

- “Record what we learned about deployment today.”
- “Remember this article’s conclusions about authentication.”
- “Tell me what Brain knows about rollback procedures.”
- “Correct the deployment concept—the old rollback procedure is wrong.”
- “Connect deployment failures with the incident-response concepts.”
- “Reflect on deployment knowledge and find conflicting facts.”
- “Review Brain, fix safe structural issues, and report anything that needs my judgment.”

## Setup

1. Resolve `brain_root` from `~/.config/brain/config.json`.
2. If the configuration is missing, ask the user where Brain should live and suggest `~/Brain` by default.
3. Create or verify the chosen directory, then store its absolute path:

   ```json
   {
     "brain_root": "/absolute/path/to/Brain",
     "ignore_dirs": []
   }
   ```

Do not read or migrate configuration from an earlier skill name.

- **Completion criterion**: `brain_root` is an absolute path in `~/.config/brain/config.json`, and the directory exists.

## Operations

### Record

Use when the user provides new durable knowledge or asks Brain to remember something.

1. **Inspect existing knowledge**: Read relevant directory indexes and search concepts before choosing where the knowledge belongs.
2. **Create or incorporate**: Create a new concept only when the knowledge does not belong in an existing one. Every concept has self-describing frontmatter:

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

3. **Index**: Add or update the concept link and description in its directory’s `index.md`.
4. **Connect**: Add clear, evidence-backed relative Markdown links to related concepts. Report each automatic connection. Suggest rather than write ambiguous or interpretive relationships.
5. **Log**: Ensure `<brain_root>/log.md` starts with `# Change Log`. Under a top-level `## YYYY-MM-DD` header (newest first), record the change with a bold action verb.
6. **Validate**: Run `python3 "${CLAUDE_SKILL_DIR}/scripts/validate.py" <brain_root>`.

- **Completion criterion**: The knowledge is incorporated into a valid concept, its parent index references it, clear connections are maintained, the current date’s log records the change, and validation passes without errors.

### Recall

Use when the user asks what Brain knows or requests a synthesis from stored knowledge.

1. **Traverse**: Read relevant `index.md` files and search for matching concepts.
2. **Synthesize**: Answer strictly from Brain by default and cite the relevant concepts with relative Markdown links.
3. **Expose gaps**: State when Brain lacks enough information. Do not silently fill gaps with model knowledge.
4. **Respect the write boundary**: External research remains read-only unless the user explicitly pairs it with Record or another storage instruction.

- **Completion criterion**: The question is answered from stored knowledge with concept citations, and gaps or outside information are clearly identified. Brain is unchanged.

### Revise

Use when the user explicitly asks to correct, restructure, or replace existing knowledge.

1. **Locate**: Read the target concept and any connected concepts affected by the requested change.
2. **Revise with evidence**: Apply only the authorized semantic change. Preserve conflicting claims when the available evidence does not resolve them.
3. **Maintain structure**: Update timestamps, indexes, clear connections, and the change log as needed.
4. **Validate**: Run `python3 "${CLAUDE_SKILL_DIR}/scripts/validate.py" <brain_root>`.

- **Completion criterion**: The requested change and its clear downstream effects are applied, logged, validated, and summarized.

### Connect

Use when relationships among concepts are the user’s primary intent. Record and Revise also perform this operation automatically for clear, evidence-backed relationships.

1. **Inspect both sides**: Read every concept participating in the proposed relationship.
2. **Connect conservatively**: Add relative Markdown links when the relationship is factual and unambiguous.
3. **Suggest ambiguity**: Report speculative, interpretive, or unsupported relationships instead of writing them.
4. **Maintain and validate**: Update affected indexes or logs as appropriate, then run the validator.

- **Completion criterion**: Supported relationships are represented by valid relative links, ambiguous relationships are presented as suggestions, and all changes are reported.

### Review / Reflect

Use when the user wants to assess the quality, consistency, completeness, currency, or structure of Brain.

1. **Validate structure**: Run `python3 "${CLAUDE_SKILL_DIR}/scripts/validate.py" <brain_root>` and collect errors and warnings.
2. **Inspect knowledge**: Look for conflicting facts, stale claims, weak or missing support, missing concepts, and useful unanswered questions.
3. **Report first**: Present findings with supporting concept links. Review / Reflect alone never changes Brain.
4. **Honor compound authorization**: If the user also requested fixes, make only the explicitly authorized changes after inspection.

Safe structural repairs are deterministic and do not change meaning, such as adding an unambiguous missing index entry or repairing a relative link with exactly one clear target. Do not choose between conflicting facts, delete or merge concepts, invent metadata requiring judgment, or rewrite claims without explicit authorization.

- **Completion criterion**: Findings and evidence are reported; authorized safe repairs are applied and summarized; ambiguous structural issues and semantic decisions remain for the user.

## Reference

### Specifications and Context

- [SPEC.md](./references/SPEC.md): Full Open Knowledge Format (OKF) specification.
- [llm-wiki.md](./references/llm-wiki.md): The original conceptual background on building self-maintaining compounding knowledge collections.

### Structural Reserved Files

- `index.md` — directory-level index providing progressive navigation.
- `log.md` — chronological log of Brain updates.

### Obsidian and Parser Compatibility

- **Link format**: Always use relative Markdown links `[label](../path/to/file.md)`.
- **Permissive consumption**: Tolerate broken links and ignore unknown frontmatter keys without throwing errors.
