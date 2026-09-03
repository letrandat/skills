---
type: Prompt
title: PR flow-diagram grill prompt
description: Portable agent prompt to grill a PR delta into flow diagrams, then walk those pictures against the code.
tags: [prompt, github, pr, review, grill, diagram, flow, portable]
timestamp: 2026-09-03
---

# PR flow-diagram grill prompt

A portable, self-contained prompt for grilling any pull request or branch diff until the reviewer can name the primary flow, what is new, what changed, how data moves, and which code to read first.

Runs on any agent harness (Claude Code, Antigravity, Cursor, Codex, web chats) without requiring local installation of specialized skills or tools.

## The Prompt

```text
Grill PR [PR_NUMBER or URL or BRANCH] until we share pictures of the change, then walk those pictures against the code.

Goal: I can name the primary flow, what is new, what changed, how data moves, and which code to read first.

1. Load the delta.
   Fetch the PR or branch diff. Group every changed file into a flow (one path from a trigger to a store or a client). Label each flow product, structure-only, or later.
   Done when: every changed file sits in one named flow. Put which flow is primary on the frontier.

2. Inventory pictures that already exist.
   Find in-repo diagrams whose subject is a named flow. Say what they already show and what the delta adds or changes.
   Done when: each named flow has a matching picture or is marked uncovered.

3. Propose views, then grill.
   Palette: architecture, workflow, sequence, dataflow, lifecycle. Each proposal has one job: what is new, what changed, or how data moves.
   - Sequence = who calls whom and what is not called.
   - Dataflow = where data sits after the write.
   - Lifecycle = states of the thing that changed.

   Grilling Protocol:
   - Work the design tree in rounds. The frontier is every decision whose prerequisites are settled.
   - Ask the whole frontier in one round using this exact format:
     ❓ **Q1** - **<question title>**: <question body, trade-offs, options>
     ➡️ <your recommended answer>
     ---
     ❓ **Q2** - **<question title>**: <question body, trade-offs, options>
     ➡️ <your recommended answer>
   - Facts are yours (fetch diff, identify callers, inventory existing files); decisions are mine. Ask the whole frontier in one round. Wait.
   - If a `CONTEXT.md` or domain glossary exists in this repository, adhere to its bounded contexts and challenge conflicting naming on the frontier.
   - Frontier starts as: which flow is primary, which types to draw, in-scope vs later (external or omit), two callers as one box or two sources, occupancy of each type's real bands/lanes.
   - Use names from the change. Keep incidental writes off the main path. Structure-only helpers stay off the flow picture unless I ask.
   Done when: the frontier is empty and each agreed view has a type and a job.

4. Draw and walk the code.
   - Visual Engine:
     1. Use `/archify` if the Archify tool/skill is installed.
     2. Otherwise, generate a standalone, self-contained HTML file with inline SVG, dark/light theme toggle, and responsive styling.
     3. If writing HTML files is prohibited or unsupported, output GitHub-compatible Mermaid diagrams (`flowchart`, `sequenceDiagram`, `stateDiagram-v2`).
   - Default output location: `docs/diagrams/pr-<num>-<flow>.html` (or project root if `docs/` is absent), confirmed on the frontier.
   - Walk after draw:
     Delivering an HTML file is not completion. Walk the HTML in read order with a code pointer (`file:line`) on every hop and a ranked list of methods to read.
     If a picture fights its type (empty bands, one cramped rail), grill occupancy again before more layout hacks.
   Done when: I can point at a hop and you can name the file:line, and I know what is product vs bookkeeping.
```

## Palette & Diagram Selection Guide

| Diagram Type | Best Used For | What it Reveals in a PR |
| :--- | :--- | :--- |
| `sequence` | Invocation ordering, protocol hops, guard conditions | Who calls whom, skipped layers, and new uncalled paths |
| `dataflow` | State mutations, payload reshaping, indexing | Where data lands after the write, deleted columns, and new side-effects |
| `lifecycle` | State machines, status transitions, TTLs | New entity statuses, transition guards, and tombstone/drain paths |
| `architecture` | Boundary crosses, module decoupling, new adapters | High-level module placement and dependency orientation |

## Agent Mechanics & Protocol Inlining

1. **Delta Flow Clustering**: Groups all changed files into cohesive end-to-end flows rather than reviewing files alphabetically or by directory.
2. **Leading Vocabulary**: Keeps the conversation grounded in *delta*, *flow*, *frontier*, *job*, *occupancy*, *product*, and *bookkeeping*.
3. **Decisions vs. Facts**: The agent computes the diff and isolates callers; the reviewer decides primary vs secondary flows and what stays off the main canvas.
4. **Code Pointer Walk**: Every hop on the diagram must be verifiable with an exact `file:line` reference before the review is marked complete.

## Example Invocation

```text
Grill PR #142 (https://github.com/myorg/myrepo/pull/142) until we share pictures of the change, then walk those pictures against the code.

Goal: I can name the primary flow, what is new, what changed, how data moves, and which code to read first.
```
