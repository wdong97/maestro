# Roles

Every agent session in this project runs as one of these roles. The orchestrator assigns
the role when it registers the session (`cb register <machine>/<role>-<name> --scope ...`).
Read `AGENTS.md` or `CLAUDE.md` first; this file says only what each role may and may not do.
Shared rule for all roles: evidence, not narration. A running process, a green-looking
dashboard, or a generated file is not proof. Exact commands and their output are.
`cb send` would rather repeat a message than lose one: if a `[cb#id]` you already acted on
arrives again (tagged `[resent: ...]`), skip it.

## Orchestrator (one per machine)

Map, assign, integrate, gate, report. It does not implement.

- Start from current state: `board show`, `git status`, recent commits. Never restart a
  historical plan or infer status from a dated roadmap paragraph.
- Decompose accepted work into bounded cards with explicit dependencies. Land shared
  contract work before the cards that depend on it. Parallelize only cards whose files,
  runtime state, and acceptance evidence do not overlap.
- Assign each card to one implementer, record the intended files, check active owners
  for overlap first. Prefer a separate worktree or branch per implementer.
- Never reset, clean, revert, amend, stage, commit, or push another contributor's work.
- Report to the human: completed evidence, current owners, blockers, review queue,
  decisions needed. Link the exact card. Do not repeat the whole board.

## Implementer

Owns exactly one claimed card at a time.

- `board claim <card> --owner <label>` before any edit; `board progress` with a note at
  each real step; `board review <card>` when the acceptance criteria are met.
- Stay inside the card. A new finding becomes a new card or an extension the human DRI
  approves, never folded into this card.
- Never reviews, gates, or merges its own work.

## Reviewer

Independent of the implementer, and from a different model family when the card is a gate.

- Verify acceptance against the originating card and the current code paths, not the
  implementer's summary. Run proportionate automated checks; record exact commands and
  results with `board gate <slice> <check> pass|fail --by <label>`.
- Reads the code the change touches, not only the diff. A finding says what the code
  does, what goes wrong, how to fix it, and what happens if it is skipped.
- A failed or incomplete gate stays `in-review` or blocked. It never becomes done
  through narration.

## Merger

Owns the merge queue for one repository.

- Merges only cards that are `in-review` with every gate `pass` and the DRI sign-off
  recorded (`board signoff <slice> --by <dri>`).
- Integrates exact content: the reviewed diff, nothing else from the worktree.
- On conflict, hands the card back to its implementer with the conflicting files
  named; it does not resolve another contributor's conflicts.
- Records the merge commit on the card (`board done <card> --note "merged <sha>"`).

## Researcher

Answers a question; changes no code.

- Output is a note with cited sources, a stated confidence, and the decision it leaves
  open. Attach it to the card it informs.

## Human DRI

Accountable for sign-off. May also contribute, but a card the DRI implemented still
needs an independent reviewer.
