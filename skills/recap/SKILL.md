---
name: recap
description: Refresh everything that may have gone stale — the PR, the jobs you started, the CI run, the threads the user linked — then report four things: the goal in the words of whoever asked, where things actually stand and what the evidence is, what's blocked on a person versus blocked on something technical, and next steps each marked as yours or theirs. Starts no new work. Use when the user asks for a recap, a re-sync, where things stand now, an update after time has passed, or a briefing before a meeting or handoff.
---

# recap — refresh the world, then report four things

A recap is for coming back after time has passed. Things you last looked at are now
stale: the PR got a review, the job finished, CI went red, someone answered in the
thread. **Refresh first, then report.** A recap built from memory is the exact failure
this skill exists to prevent.

## Step 1 — Refresh (a minute or two, no more)

Re-check anything whose state lives outside this conversation. Read-only, in parallel:

- **The PR** — `gh pr view <n> --json state,mergeable,reviewDecision,statusCheckRollup`,
  `gh pr checks <n>`. New reviews? Checks flipped? Conflicts now?
- **Jobs you started** — `ensemble jobs`, the run's log or `out.txt`, any background task
  still open, any process you left running.
- **CI / deploys** — the run for *this* commit, not the one you remember.
- **The branch** — `git fetch`, then `git status -sb` and `git log --oneline origin/main..HEAD`.
  Has the base moved under you?
- **Threads the user linked** — re-read them (Slack, issue, PR comments) for answers that
  arrived while you were away. If your runtime can't reach one, that's a line in the
  report, not a guess.
- **The files** — `git status`, and the artifacts you claimed to produce.

Time-box it. Refresh is a scan, not an investigation — if something needs digging, that's
a finding for the report, not work to do now. Say plainly what you could not refresh and
why (no access, no network, not connected).

## Step 2 — Report exactly four things

### 1. The goal, in their words

Quote the person who asked, near-verbatim. Not your restatement, not what the work turned
into. If several people asked for different things, list each with their name. If it
changed mid-flight, give the current one and what it replaced.

### 2. Where things actually stand — with the evidence

One line per item: the claim, then what proves it, then how fresh that proof is.

**Unit tests passing does not count as proven.** Nor does a clean type-check, a local
run, a green diff, or your own earlier message. Those show the code is *plausible*.

Proof is the real thing working in the real place:

- CI green on **this** commit (name the run and when).
- The endpoint answered in staging; the job completed; the file exists where it should.
- A person looked and said so — approved the PR, confirmed in the thread.
- The artifact is where the user will look for it: pushed, merged, deployed, published.

Anything short of that is **not proven** — say so in those words, and say what would
settle it. Never write "should work."

### 3. Blocked on a person vs blocked on something technical

Two separate lists; the difference decides what happens next.

- **Waiting on a person** — name who, what you need from them, how long it has waited,
  and whether they've been asked yet. "Nobody has actually been asked" is the most common
  and most useful thing a recap surfaces.
- **Blocked on something technical** — what's broken, the error, what you already tried,
  and what you'd try next. No fix now; this is a description.

If nothing is blocked, say "nothing blocked" — don't manufacture entries.

### 4. Next steps, each owned

Short list, ordered by what happens first. Tag every line **[me]** (the agent writing the
recap) or **[you]** — or a named person when it's someone else's. No line without an
owner. If a step can't start until something in
list 3 clears, say which.

## The one hard rule

**A recap starts no new work.** No fixes, no commits, no pushes, no merges, no "while I
was in there." Read-only commands only: `gh pr view` yes, `gh pr merge` no. Find a bug
mid-refresh? It goes in the report. The next step is the user's to approve — that's the
whole point of stopping here.

Everything above is agent-neutral: `git`, `gh`, and `ensemble` behave the same from any
session, and the report never assumes which model wrote it. Run it from Claude or Codex.

## When another skill fits better

- Cheap mid-session checkpoint, nothing external to refresh → `status`.
- Ending the session and clearing leftovers → `closeout`.
- What's outstanding across the whole repo, not this thread → `catch-up`.

## Example

> **Goal — in your words:** "get the export endpoint behind the feature flag so support
> can try it Monday without a deploy."
>
> **Where it stands**
> - Endpoint merged — PR #412, merged 2h ago, CI green on `a91f30c`. Proven.
> - Flag wired up — unit tests pass, but it has never run with the flag off in staging.
>   **Not proven.** A staging request with `EXPORT_V2=0` would settle it.
> - Row-limit bump — pushed to `feat/export`, no CI run yet. Not proven.
>
> **Waiting on a person**
> - Staging deploy — needs your approval in #ops. Asked 40 min ago, no reply yet.
>
> **Blocked technically**
> - Nothing.
>
> **Next steps**
> 1. [you] Approve the staging deploy, or tell me to ask someone else.
> 2. [me] Once it's up, run the flag-off request and report the result.
> 3. [me] Re-run CI on `feat/export` — blocked until the deploy lands.
