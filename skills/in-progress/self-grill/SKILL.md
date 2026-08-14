---
name: self-grill
description: Run grill-with-docs against yourself from a large up-front brief, then emit a full question log for async review.
disable-model-invocation: true
---

# Self-grill

Run `/grill-with-docs`. You are the **stand-in**: every decision grilling would put to the human, you **pick**. After each frontier, pick, check, and continue. The session ends in one **log**.

The **brief** is source of truth for stated wants, knowns, and unknowns. Gaps get the most reasonable pick, then a check.

## Rounds

Same **design tree**, **frontier**, and question shape as `/grilling`. Facts are looked up, never picked.

Each **round**:

1. Compute the frontier.
2. For each frontier question, write the options and recommended answer, then **pick** — the brief when it already chose, otherwise the recommended answer.
3. If the pick is falsifiable, check it (search, code, tests). Independent checks on the same frontier may run in parallel. A failed check **retracts** the pick and every question that hung off it. Record the failed branch. Recompute the frontier.
4. A pick that is neither in the brief nor checkable is an **assumption**. Keep going.
5. Start the next round. Stop when the frontier is empty.

## Log

When the frontier is empty, emit one log the human can annotate. Done when every question that was asked appears — held and retracted — and every proposed glossary or ADR change is listed.

For each question:

```
❓ **Q<n>** - **<title>**: <body and options>

➡️ <recommended>

✅ **Pick**: <the option>
**Why**: <one or two sentences>
**Grounding**: brief | check | assumption
**Status**: held | retracted — <what replaced it>
```

Then:

- **Assumptions** — every assumption pick, so the human can override first
- **CONTEXT.md** — proposed terms, using `/domain-modeling` format. Leave the file unchanged until the human accepts.
- **ADRs** — proposed only when the three-part test in `/domain-modeling` holds. Leave the files unchanged until the human accepts.
- **Findings** — facts the checks turned up
- **Deliverable** — if the brief asked for one, produce it from the held picks

A later message that annotates this log is a new self-grill. The annotations are the brief; contradicted picks retract.
