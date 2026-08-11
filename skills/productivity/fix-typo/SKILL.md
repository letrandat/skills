---
name: fix-typo
description: Session mode for voice-dictated prompts. Apply the fuzzy-assumption rule for the rest of this chat.
disable-model-invocation: true
---

# Fix typo

This chat is voice-dictated. On fuzzy or errors (code symbols, commands, routes, env vars, domain terms):

1. Prefix line 1 with `✨ Assuming '[fuzzy]' refers to '[target]'...`
2. Proceed immediately to execution.
