---
name: closeout
description: End a session cleanly — audit every item in the thread's scope against real evidence, report in plain English what was done, what's left, and what's deliberately not happening, then finish only the leftovers the user approves and stop. Use when the user says wrap up, close this out, are we done, ship it, what's left, or stop, and use it on yourself when you notice you're improving work nobody asked you to improve.
---

# closeout — audit, report, get approval, stop

A session ends well when the user knows exactly what they have, what they don't, and
what it would take to get the rest. It ends badly when an agent keeps finding one more
thing to improve.

**Scope is what the user asked for in this thread.** Not what would be nice, not what you
noticed along the way, not what you'd do if the repo were yours. Everything else is a
note in the report, never a task you start.

## Phase 1 — Audit against evidence

Build the item list from three sources, in this order:

1. **What they asked for** — every request in the thread, including ones a later pivot
   replaced. A request doesn't stop existing because the conversation moved on.
2. **What you promised** — "I'll do that next," "still open," "whenever you want it,"
   and any `TODO` you left in a file.
3. **What is actually there** — check, don't remember. `git status`, `git diff --stat`,
   `ls` the files you claim to have written, the test output, the process that's
   supposedly running. **Your own earlier message is not evidence.**

Then classify every item as exactly one of:

- **Done** — and you can point at the proof.
- **Left** — in scope, not finished.
- **Not doing** — superseded by their pivot, or they said no. It still gets listed.
- **Unverified** — you believe it's done but can't prove it here (needs their login,
  their browser, a deploy, a machine you're not on).

Nothing moves to Done on memory. If you can't verify it in this environment, it's
Unverified and the report says what would settle it.

## Phase 2 — Report in plain English

Short, past tense, no jargon, no hedging. Four sections, each one line per item; drop
any section that's empty except **Left**:

- **Done** — what it is and where it lives (`path:line`, a command's output, a commit).
- **Left** — what remains and how big it is: minutes, or another session.
- **Not doing** — dropped or declined, so nothing disappears quietly.
- **Needs you** — what only they can confirm or decide.

If something failed, say it failed and show the output. If tests never ran, say tests
never ran — don't write "should work."

## Phase 3 — Ask once, act zero

If **Left** is empty, skip straight to Phase 5. Never invent work to justify the audit.

Otherwise ask a single question: which of the leftovers to finish now. Recommend the
smallest set that makes the work coherent — usually the items that leave something
half-built if skipped. **The default is none**: silence closes the thread as-is. Don't
start anything while the question is open.

## Phase 4 — Finish only what was approved

- Only the approved items. Nothing adjacent, nothing "while I'm in here."
- The smallest change that completes each one. No refactors, no new abstractions, no
  reformatting of code you're touching for one line.
- Find a bug on the way? Finish the item, list the bug in the final report, leave it
  alone unless they say otherwise.
- Verify each item as you finish it, to the Phase 1 standard.
- If an approved item turns out much bigger than you reported, stop and say so before
  continuing. A wrong estimate is worth one more question.

## Phase 5 — Close it

The final message:

1. One line on the state of the work.
2. What's uncommitted, unmerged, or unshipped — with the exact command to finish it.
   Don't run it unless they asked.
3. Follow-ups worth remembering, written as a list they can paste into an issue.
4. Stop.

Stop means stop. No "want me to also," no menu of next steps, no fresh proposals. A tidy
summary followed by three new suggestions reopens the thread you just closed — that is
the single most common way this fails.

## What not to do

- Don't fix things you weren't asked to fix, however small.
- Don't polish work the user already accepted.
- Don't replay the conversation; the report is the record.
- Don't count planning, explaining, or reading as delivered work.
- Don't mark anything done that you didn't check this session.
- Don't split the approval into several questions. One question, then act.

## When this isn't the right skill

Mid-task with a clear next step? Keep working — closing early is its own failure.
If someone else is picking the work up, the report here is the starting point, but add
whatever handoff notes your team expects.

## Example report

> **Done**
> - Export endpoint added — `api/routes/export.py:41`, returns 200 on the smoke test.
> - Row limit raised to 50k — `config/limits.yaml:12`.
>
> **Left**
> - Retry on timeout: not started, ~20 minutes.
> - Docs for the new endpoint: not started, ~10 minutes.
>
> **Not doing**
> - The queue refactor we discussed — you scoped it out on Tuesday.
>
> **Needs you**
> - Staging deploy: I can't reach that host, so nothing is verified there yet.
>
> Tests: `pytest tests/export/` passed, 14 tests. The full suite hasn't run.
>
> Want me to finish the retry and the docs before we close? I'd do both — the endpoint
> is hard to use without either. Otherwise this stops here, with everything above
> uncommitted on `feat/export`.
