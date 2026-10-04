---
description: Set a goal, then loop on its own until it's met — interview, frozen evals, hillclimb with keep/revert
argument-hint: "[the goal, e.g. 'p95 of /search under 200ms']"
---

Apply the `goal-loop` skill to the goal below. If `.goal/` already exists in this
project, resume it instead of starting over (`goalctl status`).

1. **Interview** only for what's unclear, until the done criteria are checkable.
2. **Contract**: `goalctl init`, fill in `.goal/GOAL.md`, wait for the user's approval.
3. **Evals**: write `.goal/evals/run`, have a subagent write the holdout, show the
   baseline, wait for approval, then `goalctl freeze`.
4. **Loop**: `goalctl start`, then one change per `goalctl iterate` until goalctl
   reports a terminal status. Don't check in while running; block only for decisions
   the contract reserves for the user.
5. **Wrap up** with the holdout score, baseline → final, cost and wall time, and what
   was tried.

Goal: $ARGUMENTS
