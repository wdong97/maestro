---
name: status
description: Say what this session set out to do and how far along it is — the goal in one sentence, then a plain-English list of what's done, in progress, not started, and dropped. Use when the user asks where are we, what's the status, how far along are we, what have we done so far, or for a quick progress check. For a recap after time has passed — anything needing the PR, CI, jobs, or linked threads re-checked — use the `recap` skill instead. A read-only checkpoint mid-session; it reports and stops, it doesn't wrap up or start work.
---

# status — the goal, and how far along it is

A checkpoint someone can read in fifteen seconds. Not a summary of the conversation,
not a plan, not a wrap-up.

## Name the goal

One sentence, from the user's own opening ask — the outcome they wanted, not the tasks
you performed. If it moved mid-session, give the current goal and note in half a line
what it replaced. If the session never had one clear goal, say that instead of inventing
one; a wandering session is a fact worth stating.

## Check before you list

Look at what's actually there — `git status`, `git log --oneline`, the files, the last
command's output. **Your own earlier messages are not evidence.** Anything you can't
check right now is *in progress* or *unverified*, never *done*.

## The list

Bold status word, then one plain-English line. Newest-relevant first, not chronological.

```
**Goal:** <what we're trying to get to, in one sentence>

- **Done** — <what it is, and where it lives>
- **Done** — <…>
- **In progress** — <what's half-built, and what's missing from it>
- **Not started** — <in scope, untouched>
- **Dropped** — <cut, and why: they said no, or the pivot replaced it>
- **Unverified** — <believed done, can't prove it here; what would settle it>

**Where we are:** <one line — how much of the goal is reached, and what stands between
here and the rest>
```

Drop any status that has no items. Keep the whole thing on one screen: if it runs past
a dozen lines, the items are too fine-grained — group them.

## Rules

- Plain words. No jargon, no metrics, no percentages you can't defend.
- One line per item. If it needs two, it's two items or it's too much detail.
- Planning, reading, and explaining are not items. Only things that changed something.
- Don't grade generously. Half-built is *in progress*; unrun tests are not *done*.
- Don't reshape the goal to match what got finished.
- Failures get a line of their own, in the same list, said plainly.
- **Report and stop.** No question at the end, no menu of options, no starting work. If
  the user was mid-task, they can carry straight on from here.

## When another skill fits better

- Coming back after time away, where the PR, CI, jobs, or threads may have moved → `recap`.
- Ending the session, needing approval on leftovers → `closeout`.
- Closing a message with owned next actions → `next-steps`.
- Explaining what a thing *is* rather than where it stands → `eli5`.

## Example

> **Goal:** get the nightly import running without manual restarts.
>
> - **Done** — retry-on-timeout added, `jobs/import.py:88`; failed run recovered on its own last night.
> - **Done** — alert fires to #ops instead of email.
> - **In progress** — the dedupe pass runs but is slow on big files; ~4 min on the 2 GB sample.
> - **Not started** — the runbook.
> - **Dropped** — moving this to Airflow; you said not this quarter.
>
> **Where we are:** it survives a night unattended, which was the point. The dedupe
> speed is the one thing that could still wake someone up.
