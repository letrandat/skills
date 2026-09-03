# Agent Diagram-Grill Prompts

A collection of portable, zero-dependency prompts for AI coding agents (Claude Code, Antigravity, Cursor, Codex, or browser chats).

Unlike machine-bound skills, these prompts are 100% self-contained:
- **No local path dependencies**: They require no local skill files (`~/.gemini/...` or `~/.grok/...`).
- **Inlined Grilling Protocol**: Enforces relentless frontier-driven rounds, facts-vs-decisions division of labor, and shared understanding before drawing.
- **Universal Visual Rendering**: Uses Archify if available (`/archify`), with automatic fallback to standalone self-contained HTML with inline SVG, or native Mermaid diagrams.
- **Code-Grounded Traversal**: Diagram delivery is never the finish line. The agent must walk every hop against concrete `file:line` references in the codebase.

## Catalog

| Prompt | Target Scenario | Primary Views | Output |
| :--- | :--- | :--- | :--- |
| [**system-diagram-grill**](./system-diagram-grill.md) | Surveying a subsystem, service, or complex domain surface (e.g., RAG, async pipelines, ingestion). | `architecture`, `workflow`, `sequence`, `dataflow`, `lifecycle` | `docs/diagrams/<system>-<view>.html` |
| [**pr-flow-diagram-grill**](./pr-flow-diagram-grill.md) | Reviewing PRs or branch deltas by grouping changed files into named functional flows. | `sequence`, `dataflow`, `lifecycle` | `docs/diagrams/pr-<num>-<flow>.html` |
| [**ticket-solution-diagram-grill**](./ticket-solution-diagram-grill.md) | Dissecting an issue or bug into paired failure mode (As-Is) vs invariant fix (To-Be). | `sequence`, `lifecycle`, `dataflow`, `architecture` | `docs/diagrams/ticket-<id>-solution.html` |

## How to Use

1. **Copy-Paste**: Open any prompt file, copy the block under `## The Prompt`, fill in the bracketed placeholders (e.g., `[SYSTEM_NAME]`, `[PR_NUMBER]`, or `[TICKET_KEY]`), and send it to your agent.
2. **File Reference in Agent CLI**: If your harness supports file references (e.g., Cursor, Claude Code, Antigravity):
   ```text
   @prompts/system-diagram-grill.md Grill the auth subsystem in src/auth/...
   ```
3. **Piping via CLI**:
   ```bash
   cat prompts/pr-flow-diagram-grill.md | pbcopy
   ```
