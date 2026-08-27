---
name: closeout
description: End a session cleanly — name the goal the session set out to reach, audit every item in scope against real evidence, report in plain English how far the goal actually got, what's left, and what's deliberately not happening, then finish only the leftovers the user approves and stop. Use when the user says wrap up, close this out, are we done, ship it, what's left, or stop, and use it on yourself when you notice you're improving work nobody asked you to improve.
---

# closeout — audit, report, get approval, stop

A session ends well when the user knows exactly what they have, what they don't, and
what it would take to get the rest. It ends badly when an agent keeps finding one more
thing to improve.

**Scope is what the user asked for in this thread.** Not what would be nice, not what you
noticed along the way, not what you'd do if the repo were yours. Everything else is a
note in the report, never a task you start.

## Phase 1 — Audit against evidence

**First, name the goal.** One sentence, in the user's own terms, for what they came into
this thread to get — the outcome, not the task list ("the export endpoint works in
staging", not "add a route and some tests"). Take it from their opening request, not from
what you ended up doing. If it moved mid-session — they pivoted, or the first attempt
proved impossible — say what it started as, what it became, and which one the work was
measured against. If the thread never had one clear goal, say that too; a session that
wandered is a fact worth reporting, not something to tidy up.

Then build the item list from three sources, in this order:

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

Short, past tense, no jargon, no hedging. Lead with the goal, then the sections — one
line per item; drop any section that's empty except **Left**:

- **Goal** — the one sentence from Phase 1, and the pivot if there was one.
- **How far it got** — always one of these four: **met** / **mostly met, with X
  outstanding** / **partly met** / **not met**, judged against whichever goal Phase 1
  says the work was measured against. A pivot belongs on the **Goal** line, not here: it
  explains which goal you're judging, it never replaces the verdict. Add a sentence on
  what the user can actually do now that they couldn't before. The verdict follows from the **Done** list
  and nothing else: not from how much work happened, how many commits landed, or how hard
  it was. A session with ten commits that doesn't reach the goal is **not met**, and
  saying so plainly is the point of this skill.
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

1. One line on the state of the work, against the goal — met, or what it's still short of.
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
- Don't reshape the goal to fit what you achieved. The goal is what they asked for at the
  start; a smaller version of it that you happened to finish is "partly met", not "met".
- Don't mark anything done that you didn't check this session.
- Don't split the approval into several questions. One question, then act.

## When this isn't the right skill

Mid-task with a clear next step? Keep working — closing early is its own failure.
If someone else is picking the work up, the report here is the starting point, but add
whatever handoff notes your team expects.

## Example report

> **Goal:** get CSV export working end to end so support can pull a customer's rows
> without asking engineering.
>
> **How far it got:** partly met. The endpoint returns data and the limit is raised, so
> support can export by hand — but it drops long-running pulls, so the original "without
> asking engineering" isn't true yet.
>
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
