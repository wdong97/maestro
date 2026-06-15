---
name: duel
description: Run a Claude+Codex duel — both models answer the SAME prompt in side-by-side tmux panes, then the orchestrator synthesizes the single best answer. Use when the user wants a head-to-head, a second opinion, two models on one task, or to compare/merge two parallel implementations of the same change.
---

# duel — both models, same prompt, best answer

Drive the `ensemble` CLI (`ensemble` is on PATH; see the `ensemble` skill for full
docs). Protocol:

1. Pick a short kebab-case `<slug>` for the task. Read-only by default; if the
   user wants two parallel *implementations* to compare/merge, add `--rw` (each
   arm edits its own git worktree+branch — no clobber).
2. Launch (does not block):
   `ensemble duel --name <slug> [--rw] "<the user's task>"`
   This starts `claude` and `codex` in detached tmux panes, which need network.
   If you are sandboxed with network disabled, the launch or the claude arm fails
   — re-run with escalated/full access, or ensure a tmux server is already
   running outside the sandbox.
3. Tell the user how to watch: `tmux attach -t duel-<slug>` (Ctrl-b d detaches).
4. Wait for both arms: poll `~/.ensemble/duel/<slug>/claude.done` and `codex.done`
   (contents = exit code). Don't assume — check the files.
5. Read `~/.ensemble/duel/<slug>/claude.out` and `codex.out` (the clean answers;
   `.log`/`.stream` are noisy live mirrors).
6. **Synthesize** — do not paste both. State where they agree, where they differ,
   verify contested claims against the repo/tests, give ONE recommendation. For
   `--rw`, diff the `ens/<slug>/{claude,codex}` branches, pick/merge the winner,
   then `ensemble clean <slug>`.
