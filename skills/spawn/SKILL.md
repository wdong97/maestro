---
name: spawn
description: Delegate a task to a peer coding agent (Claude or Codex) running in a watchable tmux window. Use when the user wants to hand a well-specced task to the other agent and watch it work live, rather than running it headless.
---

# spawn — watchable delegation to a peer agent

Drive the `ensemble` CLI (`ensemble` is on PATH; see the `ensemble` skill for docs).

1. Choose the peer: `claude` or `codex`. From a Codex session the peer is usually
   `claude`. Add `--rw` to let it edit the target dir in place (delegation);
   omit for read-only analysis.
2. Run: `ensemble spawn <who> [--rw] "<the task>"`
   Spawning `claude` needs network; if the sandbox blocks it, re-run with
   escalated/full access (or rely on a tmux server already running outside the
   sandbox).
3. Tell the user how to watch: `tmux attach -t ensemble`, then select the new
   window. Output lands in `~/.ensemble/spawn/<name>/out.txt`.
4. When `~/.ensemble/spawn/<name>/run.done` appears (poll it), read `out.txt` and
   verify the result against the repo and tests before trusting or committing it.
   The peer's output is a suggestion, not ground truth.
