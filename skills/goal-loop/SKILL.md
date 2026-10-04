---
name: goal-loop
description: Autonomous goal-driven work loop. Clarify a goal by interviewing the user, turn it into frozen evals, then hillclimb (one change → eval → keep or git-revert → log) until the goal is met or the budget runs out. Use this whenever the user wants Claude to keep working on its own until something is achieved, such as hitting a metric (latency, accuracy, bundle size, test pass rate, benchmark score, coverage), building a large feature to an acceptance bar, "keep going until X", "hillclimb on", "optimize until", "grind on this overnight", "don't stop until it passes", or setting a goal for autonomous work, even if they never say "goal" or "loop". Also use it to resume or check on an existing .goal/ in the project.
---

# Goal loop

You run a long, autonomous improvement loop toward a goal the user cares about. There are four phases:

1. **Interview:** make the goal concrete.
2. **Contract:** write `GOAL.md` and get the user's approval.
3. **Evals:** build a harness that measures the goal, get approval, and freeze it.
4. **Loop:** hillclimb until a stop condition, then wrap up.

The user is involved in phases 1–3 and should be able to walk away during phase 4. That's the bargain: up-front clarity in exchange for autonomy. Rushing phases 1–3 makes phase 4 optimize the wrong thing very efficiently.

## Tools

- `goalctl` means `python3 ~/.claude/skills/goal-loop/scripts/goalctl.py`. Write the full command each time, because shell state doesn't persist between calls. It owns all bookkeeping: state, running evals, keep/revert via git, and the log. Let it do the keep/revert instead of doing it by hand. The determinism is the point.
- **State** lives in `<project>/.goal/`: `GOAL.md`, `evals/`, `LOG.md`, `results.tsv` and `state.json`. `goalctl init` adds `.goal/` to `.git/info/exclude`, so reverts never touch it. Because everything is on disk, the loop survives context compaction. When in doubt, re-read the files rather than trusting your memory.
- **The Stop hook** (`scripts/stop_hook.py`) blocks you from ending your turn while status is `running`, and tells you to continue. It lets you stop when status moves to `done`, `plateau`, `budget_exhausted`, `blocked`, `paused` or `stalled`. It also lets you stop after 3 turns in a row that end without an iteration, as a safety valve. Agents without this hook, such as Codex, follow the same rule on their own: keep iterating until `goalctl` reports a status other than `running`.

## Phase 0: Orient

- Run `goalctl status`. If a goal already exists, resume rather than starting over:
  - `drafting` or `frozen`: continue phase 2 or 3.
  - `running`: continue the loop.
  - `blocked`: get the user's answer, then `goalctl start`.
  - `plateau` or `budget_exhausted`: ask the user whether to extend, using `goalctl start --add-iterations N --reset-patience`.
- Check that the Stop hook is installed: `grep -q goal-loop ~/.claude/settings.json`. If it isn't, tell the user the loop won't continue on its own without it and offer `goalctl install-hook`. It's a global hook, but it does nothing unless `.goal/state.json` says `running`.
- The project must be a git repo with a clean working tree before the loop starts, because reverts are `git reset --hard`. If it isn't, ask the user. Never stash, commit or `git init` on their behalf without asking.

## Phase 1: Interview

Goal: be able to write done criteria that a script or a fixed rubric can check. Read the codebase first, so your questions are informed and you don't ask anything the code already answers.

Ask only what is genuinely unclear, batched into 1–3 rounds with `AskUserQuestion` (offer concrete options with a recommended default). What you usually need:

- **Done:** what is observably true when this succeeds?
  - For a metric: which metric, measured how and on what inputs, which direction, and what target. If they have no target, propose one.
  - For a feature: the user-visible behaviors, as checkable acceptance criteria.
- **Constraints:** what must not break or change (APIs, dependencies, existing tests, a performance floor, files that are off-limits).
- **Non-goals:** adjacent work they don't want.
- **Budget:** max iterations, an optional wall-clock limit, and how long a plateau to tolerate.
- **Escalation:** which decisions they want to make themselves (new dependencies, schema changes, deleting things). Everything else, you decide.

If the request is already precise ("get p95 of `/search` under 200ms on `bench/queries.txt` without new deps"), skip straight to the contract. Don't interview for its own sake.

Pick the mode. Use **metric** when there's one scalar to optimize. Use **feature** when "done" is a set of acceptance checks; the score is the fraction passing, and ties are kept so groundwork steps aren't reverted.

## Phase 2: Contract

```
goalctl init --slug <kebab-name> --mode metric|feature [--direction max|min] [--target N] \
             [--max-iterations 30] [--patience 8] [--hours H]
```

Fill in `.goal/GOAL.md` from the template it creates, then show it to the user and get explicit approval. This document is what you'll re-read every time you lose the thread, so make it specific. `init` can be re-run while drafting to change parameters.

## Phase 3: Evals

Read `references/evals.md` before writing the harness. It covers:

- the output contract (the last stdout line is `{"score", "passed", "checks"}`)
- correctness gates
- measuring noise to set `--min-delta`
- LLM-judge checks for subjective criteria
- the anti-gaming checklist

Steps:
1. Write `.goal/evals/run` and `chmod +x` it. Test it with `goalctl run`. For metric mode, run it 3–5 times to measure noise, then re-run `init` with an appropriate `--min-delta`.
2. Spawn a subagent with only GOAL.md as context to write the holdout set (`.goal/evals/holdout/run`). Don't read its contents yourself. A holdout you've seen is just more training data.
3. Show the user the checks and what the baseline produces. Get approval, then run `goalctl freeze`.

After the freeze, the evals are the fixed definition of success, and `goalctl` refuses to score if they change. If you find a genuine bug in an eval, don't work around it. Run `goalctl block --reason "<the bug and proposed fix>"`, stop, and only `goalctl unfreeze` after the user agrees. The temptation to "just fix the test" is exactly the failure this setup exists to prevent.

## Phase 4: Loop

Run `goalctl start`. It creates branch `goal/<slug>`, records the baseline and sets status to `running`. Then repeat:

1. **Orient.** Check the end of `.goal/LOG.md`: what's been tried, what failed and why, and which checks still fail.
2. **Hypothesize.** Pick the one change with the best expected gain per effort. Don't retry something the log shows failed unless you have a new reason, and write that reason down.
3. **Change.** Make the smallest change that tests the hypothesis. One idea per iteration keeps the signal clean: if two ideas ship together and the score drops, you learn nothing.
4. **Score.** Run `goalctl iterate --desc "<what you changed and why you expected it to help>"`. It runs the evals and then either commits (KEEP) or resets the tree (REVERT).
5. **Learn.** If the result taught you something beyond the score, run `goalctl note "<insight>"`. Future iterations, possibly after context compaction, depend on these notes.

Every ~5 iterations, step back:
- Re-read GOAL.md.
- Look at `results.tsv`.
- Ask whether you're making incremental gains on the right thing, or whether a different approach is needed.

When patience is running low, a bolder structural change is usually worth more than another micro-tweak.

Keep working without checking in. The user approved the contract so they wouldn't have to supervise. Stop only through `goalctl`:

- `goalctl block --reason "..."`: you need a decision the contract says belongs to the user, or you've found an eval bug.
- `goalctl pause --reason "..."`: the user asks you to pause.
- `goalctl` itself sets `done`, `plateau` or `budget_exhausted` when those conditions hit.

Stay inside the contract's constraints even when breaking one would raise the score. A score gained by violating a constraint is a failure the evals didn't catch.

## Wrap-up

When the loop ends, for any reason:
1. Run `goalctl run --holdout` if a holdout exists.
2. Report to the user:
   - the outcome and reason for stopping
   - baseline → final score vs. target
   - holdout score, and the gap from the main score if it's notable
   - iterations used, wall time, and cost (tokens or dollars if you can see them)
   - the key changes that moved the score (from the KEEP entries)
   - what was tried and didn't work
   - what you'd try next
   - any open questions
   Lead with whether the goal was met.
3. Leave the `goal/<slug>` branch for the user to review. Don't merge it.

Report honestly. If the holdout disagrees with the main score, or wins came from something that feels like gaming the metric, say so up front. A trustworthy "we got to 80% and here's why we stalled" beats an inflated "done".
