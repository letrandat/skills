# Recall

Read [Open Knowledge Format v0.1](../references/SPEC.md) completely when the request concerns Knowledge Bundle structure or OKF terminology. Read [LLM Wiki](../references/llm-wiki.md) completely when the user asks about Brain’s design philosophy.

1. **Traverse the source.** For stored knowledge, follow relevant `index.md` files and search for matching concepts and connected context. For design philosophy, use LLM Wiki as the source.
   - **Complete when:** the search has covered every relevant index branch and plausible matching concept, or LLM Wiki has been read completely for a philosophy request.
2. **Synthesize.** Answer from the selected source. Cite stored concepts using the shared internal-link rule in `SKILL.md`; identify conceptual background or other requested outside information separately.
   - **Complete when:** every material claim is supported by a cited concept or clearly identified outside Brain.
3. **Expose gaps.** State where the selected source lacks enough information, where its claims conflict, and what remains uncertain.
   - **Complete when:** every gap or conflict that affects the answer is visible to the user.
