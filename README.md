# maestro

A coordinated multi-agent coding workflow built on **Claude Code** + **OpenAI
Codex**. One source of truth, version-controlled, installed onto any machine with
a symlink-based `install.sh`.

## What's in here

- **`skills/`** — agent skills shared by both Claude and Codex:
  - `ensemble/` — the `ensemble` CLI (`duel`, `spawn`, `review`, `doctor`,
    `install-review-hook`): run Claude + Codex together, visible in tmux.
  - `duel/`, `spawn/`, `ensemble-review/`, `ensemble-doctor/` — Codex action-skills
    (`$duel`, etc.) wrapping the CLI.
  - `delegate/`, `delegate-fable/`, `delegate-opus/`, `delegate-codex/` —
    cost-aware orchestrator→implementer routing patterns.
- **`commands/`** — Claude Code slash commands (`/duel`, `/spawn`,
  `/ensemble-review`, `/ensemble-doctor`).
- **`hooks/pre-push`** — peer-review-before-every-push gate (portable; calls
  `ensemble` from PATH).
- **`guidelines/coding-guidelines.md`** — behavioral coding rules `@import`ed into
  every Claude (`CLAUDE.md`) and Codex (`AGENTS.md`) session.
- **`config/ensemble.toml.example`** — per-project gate config template (for the
  `conduct` pipeline).

Runtime artifacts (jobs, dispatch logs, screenshots) live in `~/.ensemble/`,
outside the repo.

## Install (any machine)

```bash
git clone <remote> ~/maestro
cd ~/maestro
./install.sh        # symlinks into ~/.claude, ~/.codex, ~/.local/bin, git hooks
ensemble doctor     # verify
```

Requires `claude`, `codex`, `tmux`, and `~/.local/bin` on PATH. The repo is the
source of truth — edit files here and they're live (symlinks); `git pull` updates
everything. Slash commands / skills load in new agent sessions.

Undo with `./uninstall.sh` (restores any `.maestro-bak` backups).

## Roadmap

- **P0 (done):** package the ensemble + delegate stack as this repo.
- **P1:** job-state + `ensemble watch` TUI — single pane over all running agents.
- **P2:** `conduct "<task>"` — plan→route→implement→verify(lint/types/tests/build/
  review/preview)→ship, with deterministic gate enforcement.
- **P3:** richer TUI (diffs, inline approve). **P4:** routing/parallelism/cost.
