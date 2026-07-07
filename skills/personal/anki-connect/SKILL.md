---
name: anki-connect
description: Interacting with Anki through the AnkiConnect local HTTP API.
disable-model-invocation: true
---

# AnkiConnect

## Preconditions

- Verify Anki is running and AnkiConnect is responding at `http://127.0.0.1:8765`.
- Verification test: `curl -sS http://127.0.0.1:8765` should return `Anki-Connect`.

## Safety Guardrails (Critical)

- **Confirmation**: Use the Ask User Question tool available in the harness to request confirmation before any modifying or destructive operation (adding, updating, deleting notes/cards/decks/models).
- **Scope**: Request confirmation only once per logical task (grouping by intent and scope).

## Reference Details

For the complete list of supported API actions and search syntax, see [REFERENCE.md](REFERENCE.md).

## Usage Templates

All requests are POST JSON-RPC. Prefer using `jq` to construct payloads.

### JSON-RPC Format

```json
{
  "action": "actionName",
  "version": 6,
  "params": {}
}
```

### curl/jq minimal template

```bash
jq -n --arg action "deckNames" --argjson version 6 '{action:$action, version:$version}' \
| curl -sS http://127.0.0.1:8765 -X POST -H 'Content-Type: application/json' -d @-
```

### Handling results and errors

```bash
curl -sS http://127.0.0.1:8765 -X POST -H 'Content-Type: application/json' -d @- \
| jq -e 'if .error then halt_error(1) else .result end'
```

### Batching multiple actions (`multi`)

```bash
jq -n --argjson version 6 \
  '{action:"multi", version:$version, params:{actions:[
    {action:"findNotes", params:{query:"deck:French"}},
    {action:"notesInfo", params:{notes:[]}}
  ]}}' \
| curl -sS http://127.0.0.1:8765 -X POST -H 'Content-Type: application/json' -d @-
```

## Recipes

### Searching and Previewing (Read-Only)
1. Use `findNotes` or `findCards` with search syntax to locate records.
2. Chain with `notesInfo` or `cardsInfo` to inspect details before proposing changes.

### Modifying Notes and Cards (Write-Only)
* **Preflight**: Perform read-only search/preview.
* **Confirmation**: Ask for user permission with the count of affected cards/notes.
* **Execution**: Run modifying actions (e.g., `addNote`, `updateNoteFields`, `updateNoteTags`, `deleteNotes`, `suspend`, `changeDeck`).
* Note: Keep the Anki browser closed during updates to prevent write conflicts.

