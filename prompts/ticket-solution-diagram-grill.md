---
type: Prompt
title: Ticket problem-solution diagram grill prompt
description: Portable agent prompt to dissect a ticket, map the failure mode to the right diagram, grill problem vs solution, and walk the proposed fix against the code.
tags: [prompt, jira, linear, issue, ticket, grill, diagram, problem-solution, portable]
timestamp: 2026-09-03
---

# Ticket problem-solution diagram grill prompt

A portable (khả chuyển, linh động), self-contained prompt for dissecting (mổ xẻ, phân tích chi tiết) any issue or ticket until the engineer can visualize the exact failure mode (As-Is), evaluate the target solution (To-Be) using the right diagram type, stress-test trade-offs on the frontier, and walk the proposed code changes before writing a single line of production code.

Runs on any agent harness (Claude Code, Antigravity, Cursor, Codex, web chats) without requiring local installation of specialized skills or tools.

## The Prompt

```text
Grill Ticket [TICKET_KEY or URL or DESCRIPTION] until we share pictures of the problem and the proposed solution, then walk those pictures against the code.

Goal: I can see exactly where and why the system fails (As-Is), verify why the proposed fix works (To-Be) using the right diagram type, understand all architectural trade-offs, and know which code to touch first.

1. Ingest the ticket and ground in code truth.
   Read the ticket. Locate the real code files, functions, and database entities involved.
   Trace the execution path from trigger (event, API, queue, cron) down to the failure point (SQL error, swallowed exception, race condition, lock contention, zombie state).
   State the broken invariant in one sentence: what the system is currently doing wrong vs what must strictly hold true.
   Done when: the failure path is isolated to specific files:lines and the broken invariant is explicitly stated.

2. Match the failure mode to the right diagram type.
   Pick the diagram type whose physics match the failure mode:
   - Sequence: Timing, message passing, out-of-order events, ACK/NACK, visibility timeouts, retries, and who calls whom.
   - Lifecycle / State: State fields, transition guards, zombie states, tombstone TTLs, and serving status vs attempt status.
   - Dataflow: Data transformations, query parameter binding, filtering, hash partitioning, chunk deletion, and multi-store consistency.
   - Architecture / Workflow: Subsystem boundaries, queue redrive/DLQ topology, deployment phases, and table lock escalation during migrations.
   Each ticket must have a paired view: Problem (As-Is: failure mechanics) and Solution (To-Be: invariant preserved).
   Done when: each view has an assigned diagram type, an As-Is focus, and a To-Be focus.

3. Grill problem vs solution on the frontier.
   Grilling Protocol:
   - Work the design tree in rounds. The frontier is every decision whose prerequisites are settled.
   - Ask the whole frontier in one round using this exact format:
     ❓ **Q1** - **<question title>**: <question body, trade-offs, options>
     ➡️ <your recommended answer>
     ---
     ❓ **Q2** - **<question title>**: <question body, trade-offs, options>
     ➡️ <your recommended answer>
   - Facts are yours (isolate failing line, verify DB schemas, trace call stack); decisions are mine. Ask the whole frontier in one round. Wait.
   - If a `CONTEXT.md` or domain glossary exists in this repository, adhere to its bounded contexts and challenge conflicting naming on the frontier.
   - Frontier starts as:
     - Root cause check: Is the ticket describing the actual root cause or just a symptom?
     - As-Is failure scenario: What specific input, concurrency, or environmental condition triggers the failure?
     - Solution trade-offs: Quick patch vs deep architectural seam; performance vs safety; storage cost vs latency.
     - Backward compatibility & rollout: Does the fix require a multi-phase migration (e.g., NOT VALID -> backfill -> validate) or handle rolling deployment without breaking running nodes?
     - Edge cases & poison pills: How does the solution handle non-retryable vs transient failures?
   - Keep incidental logic off the diagram. Focus strictly on the mechanism of failure and fix.
   Done when: the frontier is empty and we agree on the chosen diagram type and the target solution shape.

4. Draw and walk the code.
   - Visual Engine:
     1. Use `/archify` if the Archify tool/skill is installed.
     2. Otherwise, generate a standalone, self-contained HTML file with inline SVG, dark/light theme toggle, and responsive styling.
     3. If writing HTML files is prohibited or unsupported, output GitHub-compatible Mermaid diagrams (`flowchart`, `sequenceDiagram`, `stateDiagram-v2`).
   - Default output location: `docs/diagrams/ticket-<id>-solution.html` (or project root if `docs/` is absent), confirmed on the frontier.
   - Walk after draw:
     Walk the pictures in execution order:
     - Walk As-Is: point to the exact file:line where the failure happens and what state is corrupted.
     - Walk To-Be: point to each code modification (add/edit/delete) with file:line pointers and explain how the invariant is enforced.
     - Test & verification plan: describe the exact unit/integration test needed to prove the bug is dead (including edge cases like multiplicity drop or out-of-order events).
   Done when: I can point at any node/edge in the diagram and you can name the file:line, and I know exactly what code to write and test.
```

## Diagram Selection Guide (The "Right" Diagram)

| Failure Mode | Diagram Type | What As-Is Shows | What To-Be Shows |
| :--- | :--- | :--- | :--- |
| **Race condition / Out-of-order events** | `sequence` | Late event arriving after early event, overwriting newer state | Sequencer check dropping or reordering stale events |
| **Message loss / Visibility timeout** | `sequence` / `workflow` | Consumer batch loop timing out before ACK; exceptions swallowed | Individual message visibility extension, discrete ACK/NACK, DLQ path |
| **State corruption / TTL reset** | `lifecycle` | Uncontrolled transition loop (e.g., rescan resetting `marked_for_delete_at`) | Decoupled states (serving vs attempt) and terminal tombstone drain |
| **Data leak / Multiplicity drop** | `dataflow` | Chunks filtered by hash instead of ID; stale chunks left orphaned | Partitioning into stale IDs vs new chunks; exact delete query |
| **Lock contention / Zero-downtime DDL** | `workflow` / `sequence` | `ACCESS EXCLUSIVE` lock blocking live traffic; rolling deploy FK violation | Multi-stage migration (`NOT VALID` -> deploy -> batch cleanup -> `VALIDATE`) |

## Agent Mechanics & Protocol Inlining

1. **Paired Views (As-Is vs To-Be)**: Understanding a problem requires seeing why the current system fails; accepting a solution requires seeing how the exact same failure input is safely handled.
2. **Matching Failure Physics to Diagram Types**: Avoid generic boxes and arrows. If the bug is timing-based, use a sequence diagram. If the bug is state-based, use a lifecycle diagram. If the bug is data-partitioning, use dataflow.
3. **Broken Invariant as Anchor**: Anchoring the entire session to a single invariant prevents bikeshedding on secondary cleanup before the core issue is solved.
4. **Code-Grounded Walk**: Delivering an HTML file is never completion. The session finishes only when every diagram hop is mapped to concrete `file:line` locations and test scenarios.

## Example Invocation

```text
Grill Ticket SKD-1472 (asyncpg tuple parameter binding error during vector cosine search) until we share pictures of the problem and the proposed solution, then walk those pictures against the code.

Goal: I can see exactly where and why the system fails (As-Is), verify why the proposed fix works (To-Be) using the right diagram type, understand all architectural trade-offs, and know which code to touch first.
```
