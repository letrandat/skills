# Self-grill proposes domain docs; it does not write them

grill-with-docs runs domain-modeling, which updates `CONTEXT.md` as terms resolve and offers ADRs in place. A Self-Grill is for async review: the human reads one Self-Grill Log, then accepts, redoes, or changes a pick. Writing the glossary and ADRs during the run makes a Retract expensive and hides the proposal in a diff. Self-grill therefore lists proposed CONTEXT terms and ADRs in the log and leaves the files unchanged until the human accepts.

## Considered Options

- Write inline — faithful to grill-with-docs, bad for redo
- Write and also list — two sources of truth
- Propose in the log only — chosen
