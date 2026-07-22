# Review / Reflect

For a structural review, read [Open Knowledge Format v0.1](../references/SPEC.md) completely before interpreting diagnostics.

1. **Check structure when in scope.** For a structural review, run the validator once (`python3 <skill_root>/scripts/validate.py <brain_root>` per **Validator** in `SKILL.md`) and collect every error and warning. For a semantic review, identify the concepts and indexes that define the review surface.
   - **Complete when:** structural diagnostics are fully captured when applicable, and the complete semantic review surface is named.
2. **Inspect knowledge.** Look across the review surface for conflicting facts, stale claims, weak or missing support, missing concepts, and useful unanswered questions.
   - **Complete when:** every category has been checked across the full review surface and each finding has supporting concept evidence.
3. **Report findings first.** Present the findings with relative links to their supporting concepts and distinguish deterministic structural repairs from judgment calls.
   - **Complete when:** every finding, its evidence, its impact, and its repair class are visible before any changing branch acts.
4. **Hand authorized fixes to changing branches.** In a compound request, route each explicitly authorized fix through Revise, Record, or Connect as appropriate; retain the remaining items as proposals.
   - **Complete when:** every finding is either routed to a selected changing branch or left unchanged with the required user decision stated.
