---
description: Where the session stands — goal, evidence, blockers, owned next steps
argument-hint: "[what to focus on, e.g. 'the export PR']"
---

Apply the `recap` skill. Refresh before you report, and start no new work.

1. **Refresh** whatever could have gone stale, read-only and in parallel: the PR
   (`gh pr view`, `gh pr checks`), jobs you started, CI for *this* commit, `git fetch` +
   branch state, and any thread the user linked. Scale it to what's actually in play; say
   what you couldn't reach.
2. **State the goal in YOUR OWN words** — one sentence, the session-level outcome — then
   cite the user's own words as the evidence for that reading. Never lead with the quote.
3. **List where it stands**: Done / In progress / Not started / Dropped / Not proven, one
   plain line each, with what proves it. Passing unit tests is NOT proof — proof is CI
   green on this commit, the thing working where it'll be used, or a person confirming.
4. **Split the blockers**: waiting on a person (who, what, how long, whether they've been
   asked) vs blocked on something technical (error, what was tried).
5. **Next steps**, short, each tagged [me] or [you].

Report and stop. No question at the end, no new work. A bug found while refreshing is a
line in the report, not a task.

Args: $ARGUMENTS
