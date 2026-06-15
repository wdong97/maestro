---
name: ensemble-doctor
description: Run the ensemble self-check (CLIs, skill/symlinks, push hook, network reachability) and interpret the result. Use when an ensemble duel/spawn/review won't launch, or when the user wants to verify the Claude+Codex setup is wired up correctly.
---

# ensemble-doctor — environment self-check

Run `ensemble doctor` (on PATH) and report the result.

- Exit 0, no FAIL/WARN → say the ensemble is fully wired up.
- **FAIL**: explain + fix. `claude`/`codex`/`tmux` not found → install / fix PATH.
  Artifacts dir not writable → read-only sandbox; escalate or change CWD.
- **WARN**: note without alarm. ensemble not on PATH → symlink into ~/.local/bin.
  Missing a command/skill → that entry point isn't installed on that side.
  No global pre-push hook → `ensemble install-review-hook --global`. No tmux
  server → harmless; first launch starts one.
- **Network reachability** is the key line: this skill usually runs from a Codex
  session, so if `api.anthropic.com` (or `api.openai.com`) is NOT reachable, the
  sandbox blocked network for the spawned peer. Tell the user to re-run the launch
  with escalated/full access, or start one duel from the Claude side first so a
  tmux server exists outside the sandbox (then this session's panes attach to it).

End with a one-line verdict: ready, or the single most important thing to fix.
