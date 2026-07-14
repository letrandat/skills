# Agent Skills

This repository defines reusable skills and the language users employ to invoke and direct them.

## Language

**Brain**:
The user-invoked skill and managed knowledge collection that acts as a persistent second brain.
_Avoid_: Vault, repository

**Brain Root**:
The configured filesystem directory containing Brain's concepts, indexes, and change log.
_Avoid_: Storage directory, content root

**Concept**:
A single durable unit of knowledge stored as a Markdown page within Brain.
_Avoid_: Note, document

**Record**:
The Brain operation for incorporating new durable knowledge.

**Recall**:
The read-only Brain operation for retrieving and synthesizing stored knowledge.

**Revise**:
The Brain operation for intentionally changing existing knowledge.

**Connect**:
The Brain operation for creating meaningful relationships between concepts.

**Review / Reflect**:
The read-only Brain operation for inspecting consistency, conflicting facts, gaps, and structural health. It makes changes only when paired with an explicit action such as fix, correct, revise, repair, record, or connect.
