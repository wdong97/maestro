---
description: Run a Claude+Codex duel on a prompt in side-by-side tmux panes, then synthesize the best answer
argument-hint: "[--rw] <prompt>"
---

Run a duel between Claude Code and Codex on the task below, using the `ensemble`
skill/CLI. Follow this protocol exactly:

1. Pick a short kebab-case `<slug>` from the task. If the arguments start with
   `--rw`, pass `--rw` through (worktree-isolated parallel *implementation*);
   otherwise run read-only (both produce an answer/plan/review).
2. Launch without blocking:
   `ensemble duel --name <slug> [--rw] "<the task, minus any --rw flag>"`
3. Immediately tell the user the watch command: `tmux attach -t duel-<slug>`
   (left pane = Claude, right = Codex; detach with Ctrl-b d).
4. Wait for both arms WITHOUT foreground-sleeping: launch a background waiter on
   `~/.ensemble/duel/<slug>/claude.done` and `codex.done` (contents = exit code).
5. Read `~/.ensemble/duel/<slug>/claude.out` and `codex.out` (the clean answers —
   not the `.log`/`.stream` mirrors).
6. **Synthesize** — do not just paste both. State where they agree, where they
   differ, verify any contested claim against the repo/tests/fresh output, and
   give ONE merged recommendation. Treat both arms as suggestions until verified.
   For `--rw`, also `git diff` the two `ens/<slug>/{claude,codex}` branches, pick
   or merge the winner, then remind the user to `ensemble clean <slug>`.

Task: $ARGUMENTS
