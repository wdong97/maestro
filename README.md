# maestro

Make **Claude Code** and **OpenAI Codex** work as one team on your machine: they
share skills and project context, answer hard questions head-to-head, hand work to
each other, review every push, and report to live dashboards you can watch.

It's a plain git repo. `install.sh` symlinks it into `~/.claude`, `~/.codex`,
`~/.local/bin`, and your git hooks. The repo stays the single source of truth:
edits go live immediately, and `git pull` updates every machine.

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

You're set up. The rest of this page is the tour.

## What you get

**Two models, one answer — `duel`.** Claude and Codex answer the same prompt in
side-by-side tmux panes; the orchestrator reads both and synthesizes the best
result. Add `--rw` to have each implement in its own git worktree, then merge the
winner. In Claude: `/duel`. In Codex: `$duel`.

**Hand work to another model — `delegate`.** Keep planning and taste in your
current session; dispatch mechanical/bulk work to any implementer you pick:

```bash
ensemble delegate --to <model> [--eff low|medium|high|xhigh] [--ro] "<spec>"
# --to: opus | fable | sonnet | haiku | codex | gpt-5.5 | any full model id
```

It auto-routes to the Codex or Claude CLI by model name, runs in the background,
and shows in `ensemble jobs`. For a *watchable* peer in a tmux window instead, use
`ensemble spawn <claude|codex> "<task>"`.

**Review before every push.** A global `pre-push` hook has the *other* agent review
your diff and prompt before it leaves. Bypass once with `ENSEMBLE_REVIEW=0 git push`.
On demand: `ensemble review` (or `/ensemble-review`).

**See everything — `jobs` / `tail` / `dash`.** Every run (duel, spawn, delegation,
review) is listed with status, from any terminal:

```bash
ensemble jobs                 # one-shot list of all runs
ensemble tail <name|last>     # follow one run's output live
ensemble dash                 # interactive TUI: runs grouped by what needs you, live resource view (`p`), `?` for help
ensemble ps [--by rss]        # task-manager: system RAM-in-use %, agents sorted by CPU/RAM w/ %MEM + project
ensemble ps --stints          # per open session (process tree summed): RAM % of total, CPU, #procs, project
```

The dashboard groups runs into **NEEDS YOU** (just finished — recent and not yet
opened), **RUNNING**, **DONE** (older or already-handled, dimmed), and
**IDLE/RECLAIMABLE**, and rings the bell when a run finishes. It's read-only —
keystrokes never reach a live agent — with two guarded actions that both ask first:
`x` stops the selected run, `R` reaps idle sessions. (NEEDS-YOU window:
`ENSEMBLE_DASH_RECENT_MIN`, default 30.)

**Reclaim RAM — `reap` / `stop`.** Idle agents and dev servers add up. List what's
worth closing, keep the ones you still want, and close the rest:

```bash
ensemble reap --dry-run       # numbered list of idle sessions + dev servers (RAM each + total)
ensemble reap                 # keep the ones you name; close the rest on a y/N confirm
ensemble stop <name>          # gracefully stop one run (SIGTERM→SIGKILL its tree) — dash's `x`
```

`reap` never closes the session you run it from.

**Measure it — `report`.** A performance snapshot from real logged usage (reviews
run, findings raised by severity, delegation success rate, tokens). See
[PERFORMANCE.md](PERFORMANCE.md) for a committed snapshot; regenerate with:

```bash
ensemble report               # terminal summary
ensemble report --md > PERFORMANCE.md
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
