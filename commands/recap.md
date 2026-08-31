---
description: Refresh the PR, jobs, CI and linked threads, then report goal / evidence / blockers / owned next steps
argument-hint: "[what to focus on, e.g. 'the export PR']"
---

Apply the `recap` skill. Refresh before you report, and start no new work.

1. **Refresh** (a minute or two, read-only, in parallel): the PR (`gh pr view`,
   `gh pr checks`), jobs you started (`ensemble jobs`, run logs), CI for *this* commit,
   `git fetch` + branch state, and any thread the user linked. Say what you couldn't
   refresh and why.
2. **Report four things, in this order:**
   - The goal, quoted in the words of whoever asked.
   - Where things stand, each with its evidence and how fresh it is. Passing unit tests
     is NOT proof — proof is CI green on this commit, the thing working where it will be
     used, or a person confirming. Otherwise write "not proven" and what would settle it.
   - Blocked on a person (who, what, how long, whether they've been asked) vs blocked on
     something technical (error, what was tried).
   - Next steps, short, each tagged [me] or [you] (or a named person).
3. **Start nothing.** No fixes, no commits, no pushes, no merges. A bug found while
   refreshing is a line in the report, not a task.

Args: $ARGUMENTS
