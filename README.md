# maestro

Make **Claude Code** and **OpenAI Codex** work as one team on your machine: they
share skills and project context, answer hard questions head-to-head, hand work to
each other, review every push, and report to live dashboards you can watch.

It's a plain git repo. `install.sh` symlinks it into `~/.claude`, `~/.codex`,
`~/.local/bin`, and your git hooks — so the repo is the single source of truth,
edits are live, and `git pull` updates everything on every machine.

New here? **[docs/SETUP.md](docs/SETUP.md)** is the step-by-step guide for a fresh
machine (humans and agents). The short version is below.

## Quickstart (5 minutes)

You need `claude`, `codex`, `tmux`, `python3`, and `~/.local/bin` on your `PATH`.
(See SETUP if you're missing any.)

```bash
git clone git@github.com:wdong97/maestro.git ~/maestro
cd ~/maestro
./install.sh          # wires into ~/.claude, ~/.codex, ~/.local/bin, git hooks
ensemble doctor       # verify — expect "0 fail"
```

First win — ask both models the same question and get one synthesized answer:

```bash
ensemble duel "What's the simplest fix for <some real problem in this repo>?"
# watch live:  tmux attach -t duel-<name>
```

That's it — you're running the paradigm. The rest is just more of the same.

## What you get

**Two models, one answer — `duel`.** Claude and Codex answer the same prompt in
side-by-side tmux panes; the orchestrator reads both and synthesizes the best
result. Add `--rw` to have each implement in its own git worktree, then merge the
winner. In Claude: `/duel`. In Codex: `$duel`.

**Hand work to the other agent — `delegate` / `spawn`.** Keep planning and taste
where it's strongest; send mechanical/bulk work to the cheaper model. Effort scales
to the task (`--eff low|medium|high|xhigh`). Variants: `delegate-fable`,
`delegate-opus` (Claude orchestrates → Codex builds), `delegate-codex` (Codex
orchestrates → Claude builds). `ensemble spawn <agent> "<task>"` runs one peer in a
tmux window you can watch.

**Review before every push.** A global `pre-push` hook has the *other* agent review
your diff and prompt before it leaves. Bypass once with `ENSEMBLE_REVIEW=0 git push`.
On demand: `ensemble review` (or `/ensemble-review`).

**See everything — `jobs` / `tail` / `dash`.** Every run (duel, spawn, delegation,
review) is listed with status, from any terminal:

```bash
ensemble jobs                 # one-shot list of all runs
ensemble tail <name|last>     # follow one run's output live
ensemble dash                 # interactive TUI (run in a real terminal)
```

**Track the work — `board`.** A shared, server-less Kanban + roadmap board that
humans and agents both update (`board-state.json` → live `dashboard.html`):

```bash
board init            # scaffold orchestration/ into a repo
board serve           # open the live board (Board + Roadmap views)
board claim S1.api --owner you   # claim → progress → review → done, with gates + sign-off
```

**Shared coding guidelines.** `guidelines/coding-guidelines.md` is `@import`ed into
every Claude and Codex session (think-before-coding, simplicity, surgical changes).

## Verify / undo

```bash
ensemble doctor       # checks CLIs, skills, commands, hook, network, from either agent
./uninstall.sh        # remove the symlinks; restores any *.maestro-bak backups
```

## Layout

| Path | What |
|---|---|
| `skills/` | agent skills + the `ensemble` CLI (`skills/ensemble/scripts/ensemble.sh`) — shared by both agents |
| `commands/` | Claude slash commands (`/duel`, `/spawn`, `/ensemble-review`, `/ensemble-doctor`) |
| `bin/` | `board` CLI and `ensemble-tui` dashboard (symlinked onto `PATH`) |
| `board/` | the build-board template `board init` scaffolds into a project |
| `hooks/pre-push` | peer-review-before-push gate (portable; calls `ensemble` on PATH) |
| `guidelines/` | coding guidelines `@import`ed into every session |
| `config/` | per-project gate config template |

Runtime artifacts (logs, dispatch output, screenshots) live in `~/.ensemble/`,
outside the repo. Per-project board state lives in that project's `orchestration/`.

## Roadmap

- **P0 (done):** package the ensemble + delegate stack as this repo.
- **P1 (done):** observability — `ensemble jobs/tail/dash`; adaptive Codex effort;
  generalized build board.
- **P2:** `conduct "<task>"` — plan → route → implement → verify (lint/types/tests/
  build/review/preview) → ship, with deterministic gate enforcement.
- **P3:** richer dashboards (diffs, inline approve). **P4:** routing/parallelism/cost.
