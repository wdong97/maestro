---
description: Delegate a task to a peer agent (claude or codex) in a watchable tmux window
argument-hint: "<claude|codex> [--rw] <prompt>"
---

Delegate the task below to the named peer agent using the `ensemble` skill/CLI,
visible live in tmux.

1. First token of the args is the peer: `claude` or `codex`. `--rw` (optional)
   lets it edit the target dir in place (delegation); omit for read-only.
2. Run: `ensemble spawn <who> [--rw] "<the task>"`
3. Tell the user the watch command (`tmux attach -t ensemble`, then select the
   new window) and the output path `~/.ensemble/spawn/<name>/out.txt`.
4. When `~/.ensemble/spawn/<name>/run.done` appears (background-wait, don't
   foreground-sleep), read `out.txt` and verify the result against the repo and
   tests before trusting or committing it. The peer's output is a suggestion.

Args: $ARGUMENTS
