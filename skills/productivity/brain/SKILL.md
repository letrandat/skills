---
name: brain
description: Record, recall, revise, connect, and review a persistent OKF v0.1 second brain.
disable-model-invocation: true
---

## Brain Language

Invoke Brain explicitly, then describe the outcome naturally. The operation names are a guide, not command syntax.

| Operation | Choose it to | Natural requests | When selected |
| --- | --- | --- | --- |
| **Record** | Incorporate new durable knowledge. | “Remember this.” “Record what we learned today.” | [Record](./operations/record.md) |
| **Recall** | Retrieve and synthesize stored knowledge, or explain Brain’s design philosophy. | “What does Brain know about authentication?” | [Recall](./operations/recall.md) |
| **Revise** | Correct, restructure, or replace existing knowledge. | “Correct the deployment concept.” “Repair the indexes.” | [Revise](./operations/revise.md) |
| **Connect** | Represent meaningful relationships between concepts. | “Connect these ideas.” | [Connect](./operations/connect.md) |
| **Review / Reflect** | Inspect knowledge quality, support, currency, and structure. | “Review Brain’s health.” “Find conflicting facts.” | [Review / Reflect](./operations/review-reflect.md) |

**Durable** knowledge is anything the user wants kept beyond this chat (facts, locations, decisions, procedures, lasting context)—not transient scratch for the current turn alone.

When the user asks Brain to remember durable knowledge without naming an operation, select **Record**. Compound requests select every operation needed for the requested outcome.

## Authorization Boundary

- **Recall**, external research, and **Review / Reflect** are read-only. They may propose changes.
- Brain changes only what an explicit changing action authorizes: record, remember, revise, correct, fix, repair, or connect.
- Structural repair covers deterministic changes that preserve meaning, such as adding one unambiguous missing index entry or repairing a relative link with exactly one clear target.
- Substantive changes—choosing between conflicting facts, deleting or merging concepts, inventing metadata that requires judgment, or rewriting claims—require the user’s explicit authorization and sufficient evidence.
- External research may inform the response. It enters Brain only through an explicitly selected changing operation.

Authorization remains scoped in compound requests: permission to repair structure leaves substantive knowledge unchanged.

## Setup

1. **Resolve Brain Root.** Read `brain_root` from `~/.config/brain/config.json` and confirm it is an absolute path whose directory exists.
   - **Complete when:** `brain_root` resolves to an existing directory, **or** configuration is confirmed missing or invalid.
2. **First-time setup when needed.** When step 1 did not yield a valid root, read [First-time Setup](./operations/first-time-setup.md) completely and follow it.
   - **Complete when:** step 1 already succeeded, or First-time Setup has produced a valid `brain_root`.

## Shared Execution Spine

1. **Select.** Map every requested outcome to the Brain Language table above. For compound requests, select every applicable operation; run evidence-producing read-only operations before the changing operations that depend on them, and otherwise preserve the user’s requested order.
   - **Complete when:** every requested outcome belongs to a selected operation and the dependency order is explicit.
2. **Load.** Before acting, read every selected operation file completely, then read each distinct specification or conceptual reference whose stated condition applies once.
   - **Complete when:** every selected operation file and every distinct applicable reference has been read completely.
3. **Act.** Execute the selected files in dependency order, staying inside the authorization boundary and meeting each step’s completion check.
   - **Complete when:** every selected branch step is complete, and every proposed but unauthorized change is reserved for the report.
4. **Close the run.** If Brain changed, ensure `<brain_root>/log.md` starts with `# Change Log`, add one consolidated entry with a bold action verb under today’s `## YYYY-MM-DD` heading in newest-first order, run the validator once against the final Knowledge Bundle (see **Validator** below), and report every mutation, validator warning, and unresolved judgment call. A read-only run reports its answer or findings and confirms Brain remained unchanged.
   - **Complete when:** a changing run has one correctly placed log entry, final validation has no errors, and the report accounts for every mutation, warning, and unresolved judgment call; or a read-only run has reported its result and made no changes.

**Validator.** Run `python3 <skill_root>/scripts/validate.py <brain_root>`, where `<skill_root>` is the directory that contains this `SKILL.md` (the path used to load the skill). Prefer that resolved path over any host-specific environment variable.

## Shared Writing Rules

- **Internal links.** Write every internal concept link—including citations and relationships—as relative Markdown: `[label](../path/to/file.md)`.
- **Relationship rule.** Classify every proposed relationship before writing it:
  - **Supported** — the link is backed by user statement, shared evidence in both concepts, or an explicit connect request with clear endpoints. Write it as a relative internal link on each participating concept that should show the connection.
  - **Speculative**, **interpretive**, or **unsupported** — plausible but not established, or missing evidence. Do not write it into Brain; reserve it for the report with a one-line rationale.
  - A support classification is one of: supported, speculative, interpretive, unsupported.
- **Consume permissively.** Unknown frontmatter keys are valid, and broken internal links do not block reading.

## Reference

- [Open Knowledge Format v0.1](./references/SPEC.md) is the single source of truth for Knowledge Bundle structure. Operation files state when it must be loaded.
- [LLM Wiki](./references/llm-wiki.md) is the preserved conceptual background routed through Recall.
- [First-time Setup](./operations/first-time-setup.md) — load only when `brain_root` is missing or invalid.
