---
description: Run the ensemble self-check (CLIs, skill/symlinks, commands, push hook, network) and interpret the result
argument-hint: ""
---

Run `ensemble doctor` and report the result to the user.

- If it exits 0 with no FAIL/WARN, say the ensemble is fully wired up.
- For any **FAIL**, explain what's broken and the fix:
  - `claude`/`codex`/`tmux` not found → not installed or not on PATH.
  - artifacts dir not writable → read-only sandbox; escalate or change CWD.
- For any **WARN**, note it but don't alarm:
  - `ensemble not on PATH` → use the full script path or symlink it into ~/.local/bin.
  - missing a `/command` or `/prompt` → that entry point isn't installed on that side.
  - no global pre-push hook → `ensemble install-review-hook --global`.
  - no tmux server running → harmless; the first launch starts one.
- **Network reachability** is the important line: if `api.anthropic.com` or
  `api.openai.com` is NOT reachable and you're in a Codex session, the sandbox
  blocked network for the spawned peer — tell the user to re-run the launch with
  escalated/full access, or start one duel from the Claude side first so a tmux
  server exists outside the sandbox.

Then give a one-line verdict: ready, or the single most important thing to fix.
