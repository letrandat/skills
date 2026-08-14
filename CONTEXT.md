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

**Permanent Information**:
Information about a recurring principle, cause, or behavior that is likely to remain useful and compound with later learning.
_Avoid_: Durable knowledge, stable fact

**Expiring Information**:
Information tied to a particular time, state, event, measurement, version, or condition that can lose usefulness as conditions change.
_Avoid_: Temporary information, short-term information

**Uncertain Information**:
Information that cannot be classified confidently as permanent or expiring from the available context.
_Avoid_: Mixed information

**Recheck Trigger**:
An event or condition that tells you Expiring Information can be out of date and must be checked again before use.
_Avoid_: Expiration date, reminder

**What Lasts**:
The user-invoked lens for separating useful permanent information from expiring and uncertain information in an agent answer.
_Avoid_: Memory review, Brain review

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

### Grilling

**Self-Grill**:
A grill-with-docs session whose stand-in picks every decision from the brief and whose output is a Self-Grill Log.
_Avoid_: solo grill, batch grill, cell grill

**Brief**:
The up-front dump of knowns, unknowns, and wants that the stand-in treats as source of truth.
_Avoid_: prompt dump, context dump

**Stand-in**:
The agent answering frontier questions in place of the human.
_Avoid_: simulated user, persona

**Retract**:
The act of unsettling a pick and every question that depended on it after a check fails.
_Avoid_: undo, rollback

**Self-Grill Log**:
The review artifact of a Self-Grill: every question, its options, pick, why, grounding, and status.
_Avoid_: transcript, report

**Assumption**:
A pick that is neither grounded in the brief nor checked.
_Avoid_: guess
