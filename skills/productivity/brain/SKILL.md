---
name: brain
description: Record, recall, revise, connect, and review a persistent OKF v0.1 second brain.
disable-model-invocation: true
---

## Brain Language

Invoke Brain explicitly, then describe the outcome naturally. The operation names are a guide, not command syntax.

| Operation | Choose it to | Natural requests | When selected |
| --- | --- | --- | --- |
| **Record** | Incorporate new durable knowledge. | “Remember this.” “Record what we learned today.” | Read [Record](./operations/record.md) completely before acting. |
| **Recall** | Retrieve and synthesize stored knowledge, or explain Brain’s design philosophy. | “What does Brain know about authentication?” | Read [Recall](./operations/recall.md) completely before acting. |
| **Revise** | Correct, restructure, or replace existing knowledge. | “Correct the deployment concept.” “Repair the indexes.” | Read [Revise](./operations/revise.md) completely before acting. |
| **Connect** | Represent meaningful relationships between concepts. | “Connect these ideas.” | Read [Connect](./operations/connect.md) completely before acting. |
| **Review / Reflect** | Inspect knowledge quality, support, currency, and structure. | “Review Brain’s health.” “Find conflicting facts.” | Read [Review / Reflect](./operations/review-reflect.md) completely before acting. |

When the user asks Brain to remember durable knowledge without naming an operation, select **Record**. Compound requests select every operation needed for the requested outcome.

## Authorization Boundary

- **Recall**, external research, and **Review / Reflect** are read-only. They may propose changes.
- Brain changes only what an explicit changing action authorizes: record, remember, revise, correct, fix, repair, or connect.
- Structural repair covers deterministic changes that preserve meaning, such as adding one unambiguous missing index entry or repairing a relative link with exactly one clear target.
- Substantive changes—choosing between conflicting facts, deleting or merging concepts, inventing metadata that requires judgment, or rewriting claims—require the user’s explicit authorization and sufficient evidence.
- External research may inform the response. It enters Brain only through an explicitly selected changing operation.

Authorization remains scoped in compound requests: permission to repair structure leaves substantive knowledge unchanged.

## Setup

Brain’s configuration source is `~/.config/brain/config.json`; configurations under earlier skill names are unrelated.

1. **Resolve Brain Root.** Read `brain_root` from `~/.config/brain/config.json` and confirm it is an absolute path whose directory exists.
   - **Complete when:** `brain_root` resolves to an existing directory, or configuration is confirmed missing or invalid.
2. **Choose a root when needed.** When configuration is missing or invalid, ask where Brain should live, suggest `~/Brain`, and create or verify the chosen directory.
   - **Complete when:** valid existing configuration needs no choice, or the user has chosen a directory that exists.
3. **Store replacement configuration when needed.** When setup required a choice, write the absolute path to `~/.config/brain/config.json`:

   ```json
   {
     "brain_root": "/absolute/path/to/Brain"
   }
   ```

   - **Complete when:** valid existing configuration is unchanged, or rereading the replacement yields the chosen absolute `brain_root` and the directory exists.

## Shared Execution Spine

1. **Select.** Map every requested outcome to the Brain Language table above. For compound requests, select every applicable operation; run evidence-producing read-only operations before the changing operations that depend on them, and otherwise preserve the user’s requested order.
   - **Complete when:** every requested outcome belongs to a selected operation and the dependency order is explicit.
2. **Load.** Before acting, read every selected operation file completely, then read each distinct specification or conceptual reference whose stated condition applies once.
   - **Complete when:** every selected operation file and every distinct applicable reference has been read completely.
3. **Act.** Execute the selected files in dependency order, staying inside the authorization boundary and meeting each step’s completion check.
   - **Complete when:** every selected branch step is complete, and every proposed but unauthorized change is reserved for the report.
4. **Close the run.** If Brain changed, ensure `<brain_root>/log.md` starts with `# Change Log`, add one consolidated entry with a bold action verb under today’s `## YYYY-MM-DD` heading in newest-first order, run `python3 "${CLAUDE_SKILL_DIR}/scripts/validate.py" <brain_root>` once against the final Knowledge Bundle, and report every mutation, validator warning, and unresolved judgment call. A read-only run reports its answer or findings and confirms Brain remained unchanged.
   - **Complete when:** a changing run has one correctly placed log entry, final validation has no errors, and the report accounts for every mutation, warning, and unresolved judgment call; or a read-only run has reported its result and made no changes.

## Shared Writing Rules

- Write every internal concept link—including citations and relationships—as relative Markdown: `[label](../path/to/file.md)`.
- Write supported, unambiguous relationships; reserve speculative, interpretive, or unsupported candidates for the report.
- Consume permissively: unknown frontmatter keys are valid, and broken internal links do not block reading.

## Reference

- [Open Knowledge Format v0.1](./references/SPEC.md) is the single source of truth for Knowledge Bundle structure. Operation files state when it must be loaded.
- [LLM Wiki](./references/llm-wiki.md) is the preserved conceptual background routed through Recall.
