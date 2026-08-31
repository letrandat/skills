---
name: sumup
description: Sum up the session so far in one sentence.
disable-model-invocation: true
---

Reply with exactly one plain-text line:

Sum up — {sentence}

The sentence is ~25–40 words, in the language of the user's own chat messages, with code identifiers verbatim. Shape: <lead>: <concrete specifics — file, flag, behavior, endpoint>.

Lead:
- "You asked …" if the session was mainly questions, walkthroughs, or review with no landed change.
- "We <past-tense verb> …" if the agent implemented, fixed, merged, or changed code, config, or docs ("We fixed …", "We merged …", "We wired …").
- "You had just begun this session." if almost nothing happened.

Style only (adapt to this session):

You asked how retries work in the payment client: exponential backoff in `billing/retry.rs`, max 5 attempts, 429s only.

We fixed the flaky integration test: race in `queue_worker` shutdown by awaiting the drain channel before exit.

Use only what this session already contains. No tools.
