---
name: sharpen-prompt
description: Turn a rough coding request into a short poteto-mode prompt with a goal, a guard, and a done-check.
disable-model-invocation: true
---

# Sharpen a prompt

Hand back one short prompt that poteto-mode can run without guessing. The user decides when to run it.

poteto-mode's playbooks already add the ritual: reproduce first, measure first, verify on the real surface, show the evidence. A sharp prompt carries only what no playbook can know, in three slots:

- **Goal.** The behavior wanted, or the exact symptom and when it shows up.
- **Guard.** What must stay the same.
- **Done-check.** An input or action in this repo and the result that means done: a real command, a named sample, a user flow, a target number on a named workload.

## Steps

1. Choose the kind: Bug, Feature, Refactor, Perf, or Question. Done when one row of the table fits. A request with independent outcomes becomes one prompt per outcome.
2. Fill each slot from the repo before asking anyone. Read the repo for the real command, script, test file, fixture or sample directory, and entry point. When the repo already does what the request asks, say so and ask what is missing. Done when each slot holds a concrete name from the repo or is marked for the user.
3. Ask the user, in one message, for the slots the repo can't answer. Ask at most three questions. A preference or a target may carry your best default. Facts about the user's incident (symptom, trigger, observed behavior) come only from the user and remain `<blank>` until answered. Repo behavior may come from cited source or test evidence. Done when every slot holds an answer, an accepted default, or a marked blank.
4. Write the prompt and its sources (format below). Done when every filled slot names something a person could point at, and every done-check states its input or action and the expected result. A mood word (better, cleaner, faster, properly, robust) means the slot is still empty. A prompt with a blank is a draft; say which answer finishes it.

| Kind | Goal | Guard | Done-check |
|---|---|---|---|
| Bug | Symptom, trigger, and where it shows | Nearby behavior that works today | The original failure passes on the same surface |
| Feature | The new behavior | Existing output or behavior that stays identical | The real command or flow on a named sample gives the new result, and the old path still gives the old one |
| Refactor | The target structure | Zero behavior change | Output on named inputs is identical before and after |
| Perf | Metric, named workload, and target | Correctness stays the same | The metric reaches the target on that workload |
| Question | The question | No code changes | The answer cites files |

Two kinds route ambiguously, so their prompt ends with the words that pin the playbook: Bug with `repro first, then fix and verify`, Question with `don't change any code yet`. When this replaces an active task, prepend `new task.`

Unattended work ("I'm going to bed", "run until done") keeps its kind and adds a pass/fail finish condition, a fresh worktree, `keep a decision log`, and a stop-and-report escape: `if you're truly stuck, stop and write up why`.

## Format

```text
/pstack:poteto-mode <goal>. <guard>. <done-check>.
```

In Codex, start with `Use pstack:poteto-mode.` instead. Under the prompt, list each slot with its source: `repo: <path or command>`, `you: <answer>`, `default: <assumption>`, or `blank: <question>`.

## Examples

These come from a repo that has these files. Use the real names from the current repo.

Rough: "the export is broken, duplicates sometimes"

User answers: "Duplicates occur when a retry lands mid-run; single-attempt exports work; tests/export_retry_test.py reproduces it."

```text
/pstack:poteto-mode the export writes duplicate rows when a retry lands mid-run. single-attempt exports stay unchanged. the retry case in tests/export_retry_test.py goes from failing to passing. repro first, then fix and verify.
```

Rough: "add json to export"

```text
/pstack:poteto-mode add a --json flag to the export command. text output stays byte-identical. on samples/project/, --json output parses with jq and plain output matches the current output.
```
