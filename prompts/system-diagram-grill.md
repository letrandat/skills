---
type: Prompt
title: System diagram grill prompt
description: Portable agent prompt to survey a system or domain surface into diagrams, grill boundaries and trade-offs, and walk the pictures against the codebase.
tags: [prompt, system, architecture, grill, diagram, dataflow, portable]
timestamp: 2026-09-03
---

# System diagram grill prompt

A portable, self-contained prompt for surveying, grilling, and visualizing any system, subsystem, or complex domain (e.g., RAG, messaging backbone, ingestion pipeline) until the engineer or reviewer can name the primary and secondary flows, boundaries, data transformations, and exact code pointers.

Runs on any agent harness (Claude Code, Antigravity, Cursor, Codex, web chats) without requiring local installation of specialized skills or tools.

## The Prompt

```text
Grill [SYSTEM_NAME or SCOPE_PATH] until we share pictures of the system's architecture, dataflow, and runtime execution, then walk those pictures against the code.

Goal: I can name the primary flow(s), ingress/egress boundaries, data transformations and storage states, error/reconciliation loops, and exact code entry points.

1. Survey the system surface.
   Inspect the scope path and entry points (APIs, WebSocket gateways, queues, workers, timers). Group all components into cohesive flows (e.g., synchronous serving/query flow, asynchronous ingestion/event flow, background reconciliation/drain). Label each flow primary, secondary, or out-of-scope.
   Done when: every key module in scope sits in one named flow. Put which flow is primary on the frontier.

2. Inventory existing documentation and diagrams.
   Find in-repo diagrams, ADRs, and markdown specs covering this system. Identify what is already documented, what is stale, and where the blind spots are.
   Done when: each named flow is mapped to an existing picture or marked uncovered.

3. Propose views, then grill.
   Palette: architecture, workflow, sequence, dataflow, lifecycle. Each proposal has one job: system topology/boundaries, end-to-end user/event journey, call coordination, data mutation/projection, or entity states.
   - Architecture = topological cut and system boundaries (Transports, Orchestrators, Adapters, external dependencies).
   - Workflow / Sequence = step-by-step trigger-to-client execution, who calls whom, branching conditions, and what is skipped.
   - Dataflow = payload transformations, hashing/enrichment, chunking, and storage resting states.
   - Lifecycle = state machines of durable entities (e.g., document/job statuses, retention, tombstone/drain).

   Grilling Protocol:
   - Work the design tree in rounds. The frontier is every decision whose prerequisites are settled.
   - Ask the whole frontier in one round using this exact format:
     ❓ **Q1** - **<question title>**: <question body, trade-offs, options>
     ➡️ <your recommended answer>
     ---
     ❓ **Q2** - **<question title>**: <question body, trade-offs, options>
     ➡️ <your recommended answer>
   - Facts are yours (inspect codebase, files, symbols yourself); decisions are mine. Ask the whole frontier in one round. Wait.
   - If a `CONTEXT.md` or domain glossary exists in this repository, adhere to its bounded contexts and challenge conflicting naming on the frontier.
   - Frontier starts as: primary vs secondary flows, system cut/boundary level, in-scope vs external/mocked dependencies, granularity of internal nodes vs grouping, error/fallback paths to visualize.
   - Use real symbols and names from the codebase. Keep incidental bookkeeping off the main path.
   Done when: the frontier is empty and each agreed view has a type, a target filename, and a single crisp job.

4. Draw and walk the code.
   - Visual Engine:
     1. Use `/archify` if the Archify tool/skill is installed.
     2. Otherwise, generate a standalone, self-contained HTML file with inline SVG, dark/light theme toggle, and responsive styling.
     3. If writing HTML files is prohibited or unsupported, output GitHub-compatible Mermaid diagrams (`flowchart`, `sequenceDiagram`, `stateDiagram-v2`).
   - Default output location: `docs/diagrams/<system>-<view>.html` (or project root if `docs/` is absent), confirmed on the frontier.
   - Walk after draw:
     Delivering an HTML file is not completion. Walk the HTML in execution order with a code pointer (`file:line`) on every hop and a ranked list of key methods to inspect.
     If a picture fights its type (empty bands, cramped layout, tangled crossing lines), grill occupancy again before layout hacks.
   Done when: I can point at any node or hop and you can name the exact file:line and explain its domain responsibility.
```

## Palette & Diagram Selection Guide

| System Dimension | Diagram Type | What it Shows | Example |
| :--- | :--- | :--- | :--- |
| **Topology & Boundary Cut** | `architecture` | Boundary separation across Transports, Orchestrators, Adapters, and external third parties | Gateway $\to$ Orchestrator $\to$ VectorDB/BlobStore/LLM |
| **Request / Event Journey** | `workflow` / `sequence` | Trigger to response path, conditional branches, skip-layer guards, and timeouts | Pipeline execution (Router $\to$ Fetch $\to$ Guard $\to$ Agent) |
| **Data Ingestion & Mutation** | `dataflow` | Stage-by-stage payload transforms, hashing gates, chunking, and index mutations | Blob doc $\to$ Chunker $\to$ SHA-256 gate $\to$ Embed $\to$ `my_table` |
| **Entity State Transitions** | `lifecycle` | Discrete states, entry/exit guards, TTLs, and cleanup timers | Record lifecycle (`active` $\to$ `pending_delete` $\to$ tombstone drain) |

## Agent Mechanics & Protocol Inlining

1. **Self-Contained Grilling**: Inlines the core tenets of the Grilling protocol (`❓ Q / ➡️ Rec`, rounds, frontier) so any agent adheres to structured interviewing without requiring external files.
2. **Flow Clustering over Raw Files**: Grouping files into cohesive functional flows before diagramming prevents cognitive overload across large repositories.
3. **One Job Per View**: Separates topology, execution flow, data transformation, and entity lifecycle into dedicated views rather than cramming everything into one cluttered canvas.
4. **Code-Grounded Traversal**: Delivering diagrams is not the finish line. The session completes only when every hop is backed by a verified `file:line` pointer.

## Example Invocation

```text
Grill the Search Subsystem in my-service (src/services/search/ and src/api/v1/search/handler.py) until we share pictures of the system's architecture, dataflow, and runtime execution, then walk those pictures against the code.

Goal: I can name the primary flow(s), ingress/egress boundaries, data transformations and storage states, error/reconciliation loops, and exact code entry points.
```
