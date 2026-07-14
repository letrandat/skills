# Agent Skills

This repository defines reusable skills and the language users employ to invoke and direct them.

## Language

**Brain**:
The user-invoked conversational interface for working with an OKF v0.1 Knowledge Bundle using familiar second-brain language. Brain translates user intent into actions on OKF artifacts without renaming or extending OKF concepts, structures, or rules.
_Avoid_: Format, profile, framework

**Brain Language**:
The user-facing vocabulary accepted by Brain. It includes familiar second-brain phrases and OKF terminology; users can adopt OKF terms at their own pace. Brain uses the precise OKF term when it clarifies an artifact or validation finding, without requiring the user to use that term.
_Avoid_: Separate schema, mandatory OKF vocabulary

**Knowledge Bundle**:
The OKF v0.1 directory tree containing concepts and reserved structural files.
_Avoid_: Brain profile, Brain format

**Brain Root**:
The configured filesystem directory containing the Knowledge Bundle. It is the ownership boundary: Concepts within it belong to the bundle, while referenced files and websites outside it are external sources.
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
