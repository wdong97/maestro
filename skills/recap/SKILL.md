---
name: recap
description: Say where a session stands — the session-level goal stated in your own words and cited to the user's, then what's done, in progress, blocked on a person, blocked on something technical, and what happens next, each step owned. Refreshes anything that may have gone stale first (PR, CI, jobs, linked threads) and starts no new work. Use when the user asks for a recap, a status, a progress check, where are we, how far along are we, what have we done so far, an update after time away, or a briefing before a meeting or handoff.
---

# recap — where the session stands, and what it's waiting on

Readable in fifteen seconds. Not a summary of the conversation, not a plan, not a
wrap-up. It reports and stops.

## 1. Refresh what could be stale (a minute at most)

Anything whose state lives outside this conversation has moved since you last looked.
Re-check it first, read-only, in parallel:

- **The PR** — `gh pr view <n> --json state,mergeable,reviewDecision,statusCheckRollup`,
  `gh pr checks <n>`. New reviews? Checks flipped? Conflicts now?
- **Jobs you started** — `ensemble jobs`, the run's log, any background task still open.
- **CI / deploys** — the run for *this* commit, not the one you remember.
- **The branch** — `git fetch`, then `git status -sb` and `git log --oneline @{u}..HEAD`.
- **Threads the user linked** — answers may have arrived while you were away. If your
  runtime can't reach one, that's a line in the report, not a guess.
- **The files** — `git status`, and the artifacts you claim to have produced.

Scale this to what's actually in play. Nothing outside the session? Say so in half a line
and move on — then this is just a fast checkpoint. Never turn refresh into an
investigation: something that needs digging is a finding for the report, not work to do.

## 2. The goal — your sentence, their words as the citation

**State the session-level goal in your own words**, as one sentence: what this session is
actually for, at the altitude of an outcome. Then cite the user's own words as the
evidence for that reading — short fragments, quoted, in parentheses.

Never lead with the raw quote. A transcript line is what they typed at one moment; the
goal is the through-line across everything they've asked, and naming it is your job. The
citation is there so they can check your reading against what they actually said.

> **Goal:** make the push gate fail closed on every path, and get both agents seeing the
> same skills. *(from "ok please fix" and "make sure codex has access to all these skills")*

Rules for the sentence:

- One outcome, not a task list. "Support can export without engineering", not "add a
  route, raise the limit, write tests".
- Their words govern. If your sentence and the quotes don't sit comfortably together,
  the quotes are right and the sentence is wrong — rewrite it.
- Cite two or three fragments at most, and don't stitch them into something nobody said.
- The goal moved? Say what it is now and what it replaced, in the same sentence.
- Genuinely no single goal? Say that. A session that wandered is a fact, not a gap to fill.

## 3. Where it stands — the list, with evidence

Bold status word, one plain-English line, newest-relevant first. Drop any status with no
items; keep the whole thing on one screen.

```
- **Done** — <what it is, where it lives, and what proves it>
- **In progress** — <what's half-built, and what's missing>
- **Not started** — <in scope, untouched>
- **Dropped** — <cut, and why: they said no, or a pivot replaced it>
- **Not proven** — <believed done, no evidence yet; what would settle it>
```

**Passing unit tests is not proof.** Nor is a clean type-check, a local run, a green
diff, or your own earlier message — those show the code is *plausible*. Proof is the real
thing working where it will be used: CI green on **this** commit, the endpoint answering
in staging, the job completing, a person confirming, the artifact where the user will
look for it. Anything short of that is **Not proven**, in those words, with what would
settle it. Never write "should work". If tests never ran, say tests never ran.

## 4. Blocked on a person vs blocked on something technical

Two lists, because the difference decides what happens next.

- **Waiting on a person** — who, what you need, how long it's waited, and **whether
  they've actually been asked**. "Nobody has been asked yet" is the most useful thing a
  recap surfaces.
- **Blocked technically** — what's broken, the error, what you already tried, what you'd
  try next. A description, not a fix.

Nothing blocked? Say "nothing blocked" — don't manufacture entries.

## 5. What happens next, each step owned

Short, ordered by what comes first, every line tagged **[me]** (the agent writing this)
or **[you]** — or a named person. No line without an owner. If a step can't start until
something in §4 clears, say which.

Then stop. **A recap starts no new work**: no fixes, no commits, no pushes, no merges, no
"while I was in there". Read-only commands only — `gh pr view` yes, `gh pr merge` no. A
bug found while refreshing is a line in the report. The next move is the user's.

## Rules

- Check, don't remember. Your own earlier messages are not evidence.
- One line per item; if it needs two, it's two items or it's too much detail.
- Planning, reading, and explaining are not items. Only things that changed something.
- Don't grade generously: half-built is *in progress*, unrun tests are not *done*.
- Failures get their own line, said plainly.
- No closing question, no menu of options. If the user was mid-task, they carry on.

## When another skill fits better

- Ending the session and clearing leftovers with approval → `closeout`.
- What's outstanding across the whole repo rather than this thread → `catch-up`.
- Explaining what something *is* rather than where it stands → `eli5`.

## Example

> **Goal:** get the nightly import running unattended so nobody is woken by it.
> *(from "it keeps dying at 3am" and "I don't want to babysit this")*
>
> Refreshed: PR #218, CI on `a91f30c`, last night's run log. Nothing else external.
>
> - **Done** — retry-on-timeout, `jobs/import.py:88`. Proven: last night's run recovered
>   on its own, no page.
> - **Done** — alerts go to #ops instead of email. Proven: test alert landed there.
> - **In progress** — dedupe pass runs but takes ~4 min on the 2 GB sample.
> - **Not proven** — the 6h-timeout path. Unit tests pass; it has never run for 6 hours.
> - **Dropped** — moving to Airflow; you said not this quarter.
>
> **Waiting on a person**
> - Staging deploy needs your approval in #ops. Asked 40 min ago, no reply.
>
> **Blocked technically**
> - Nothing.
>
> **Next**
> 1. [you] Approve the deploy, or tell me to ask someone else.
> 2. [me] Once it's up, run the 6h path overnight and report what happened.
> 3. [me] Profile the dedupe pass — blocked until the deploy lands.
