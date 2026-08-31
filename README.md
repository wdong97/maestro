# maestro

Make **Claude Code** and **OpenAI Codex** work as one team on your machine: they
share skills and project context, answer hard questions head-to-head, hand work to
each other, review every push, and report to live dashboards you can watch.

It's a plain git repo, symlinked into your agent config rather than installed as a
package — so the repo stays the single source of truth: edits go live immediately, and
`git pull` updates every machine.

## Quickstart

You need `claude`, `codex`, `tmux`, and `python3` installed, plus `~/.local/bin` on your
`PATH`. Linux and WSL2 run everything; macOS runs everything except the resource views
(`ps`, `reap`, `stop`, and the RAM/CPU panes), which read Linux `/proc`.

```bash
git clone https://github.com/wdong97/maestro.git ~/maestro
cd ~/maestro && ./install.sh
```

That symlinks the repo into `~/.claude`, `~/.codex`, `~/.local/bin`, and your git hooks,
then runs `ensemble doctor` for you — expect `0 fail`. It also sets git's global
`core.hooksPath` so every repo gets the pre-push review; `./install.sh --no-hook` skips
that and touches no git config, and `./uninstall.sh` puts it back exactly as it was.
[docs/SETUP.md](docs/SETUP.md) walks through each step and what to do when one fails.

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
# --to: opus | fable | sonnet | haiku | codex | any full model id
```

Friendly names aren't version-pinned — they pass through to each CLI, which resolves
them to its own current latest (`codex` uses your `~/.codex/config.toml` model), so
`--to opus` always means today's Opus. Pass a full id to pin a specific version.

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
ensemble web [port] [--lan] [--board DIR …]   # browser app: runs + kanban tabs (watch + stop/reap, token-gated)
ensemble ps [--by rss]        # task-manager: system RAM-in-use %, agents sorted by CPU/RAM w/ %MEM + project
ensemble ps --stints          # per open session (process tree summed): RAM % of total, CPU, #procs, project
```

`web` is the whole thing in a browser. The **Runs** tab groups every run into **NEEDS
YOU** (just finished, not yet opened), **RUNNING**, **DONE**, and **IDLE/RECLAIMABLE** —
live resource gauges, click a run to expand its output, **stop** buttons on live runs,
and a reclaim panel (select all or none, uncheck what to keep, close the rest). Each
`--board DIR` adds a color-coded **project tab** — a **Board** (kanban) and **Roadmap**
(slices, gates, sign-off) read from `DIR/orchestration/board-state.json`, remembered once
registered — and runs working inside that project are tinted with its color. Every data
and action call is gated by a token printed at startup, and it binds `127.0.0.1` unless
you pass `--lan` (for a browser on another host, e.g. WSL → Windows).

```bash
ensemble web --lan --board ~/proj-a --board ~/proj-b   # runs cockpit + a tab per project board
```

`dash` is the same lanes in a terminal, and rings the bell when a run finishes. It's
read-only — keystrokes never reach a live agent — apart from two actions that both ask
first: `x` stops the selected run, `R` reaps idle sessions. (NEEDS-YOU window:
`ENSEMBLE_DASH_RECENT_MIN`, default 30.)

Runs get a short, readable **auto-name** at launch — a fast `claude` (haiku) call turns
the prompt into a slug like `auth-tokenstore-refactor`. Display-only, the run's stable id
is unchanged; disable with `ENSEMBLE_AUTONAME=0`.

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

**Stay out of each other's way — `/standup`.** Trade status with every live agent
session in the repo: each ping declares your own slice *and* asks for theirs, so the
overlaps surface before two agents edit the same file. `peers.sh` shows the collision
surface for free (no session is interrupted); the pings fill in intent; and when your
slice lands you tell the peers you blocked that their file is free again.

```bash
~/.claude/skills/standup/scripts/peers.sh --repo   # who's live in this repo, HARD vs SOFT overlap
/standup                                          # declare + ask every session in this repo, report the split
/standup all                                      # widen to every agent on the machine
/standup done "auth refactor landed on main"      # tell the peers you constrained that they're unblocked
```

**Write for the reader — `/plain-docs`.** A shared writing skill for anything a person
reads: READMEs, setup guides, release notes, proposals, runbooks. It's team-neutral —
your style guide wins — and both agents get it.

```bash
/plain-docs docs/SETUP.md            # revise a draft, keeping the author's voice
/plain-docs "release note for v2 auth changes"   # draft one from scratch
/plain-docs README.md --check        # review against the checklist, change nothing
```

**Explain it in plain words — `/eli5`.** For when an agent just did something and you
want the short true version: what happened, one everyday analogy, and the decision it
leaves you with. It re-tells, it never redoes — the facts and the plan stay put.

```bash
/eli5                                # explain the last thing the agent said or did
/eli5 hooks/pre-push                 # explain a file, an error, a term, a command
```

**Come back to it — `/recap`.** For picking work up after time has passed. It spends a
minute refreshing what's gone stale — the PR and its checks, jobs you started, CI for the
current commit, the branch, the threads you linked — then reports four things and nothing
else: the goal quoted in your words, where each item stands *with its evidence*, what's
blocked on a person vs blocked on something technical, and next steps each tagged `[me]`
or `[you]`. Passing unit tests don't count as proof; CI green on this commit, the thing
working where it'll be used, or a person confirming, do. It starts no new work — a bug it
finds is a line in the report. In Claude: `/recap`. In Codex: `$recap`.

**Where are we — `/progress`.** A fifteen-second checkpoint you can run any time: the
goal of the session in one sentence, then a plain list of what's done, in progress, not
started, and dropped, and one line on what stands between here and the goal. It reports
and stops — no questions, no new work — so you can carry straight on.

```bash
/progress                            # the goal + where it stands
/progress just the API work          # narrow it
```

(The skill is `status`; the command is `/progress` because Claude Code owns `/status`.
Both new skills are symlinked into `~/.claude` **and** `~/.codex`, so either agent can use them.)

**End the session — `/closeout`.** For when the work is done but the agent keeps finding
one more thing to improve. It names the goal you started the thread with and says how far
it actually got, audits the rest of the scope against what's on disk, reports done / left
/ not doing / needs you in plain English, finishes only the leftovers you approve, and
then stops.

```bash
/closeout                            # audit, report, ask once, close
```

**Land every update — `/next-steps`.** Ends an update the way you'd want it: what it
means in plain words, then at most three next steps, each with an owner and a size — or
an explicit "nothing needed from you." No more asking "ok, what's next?"

```bash
/next-steps                          # summarize + state the next steps for what just happened
```

## Verify / undo

```bash
ensemble doctor       # checks CLIs, skills, commands, helper bins, hook, platform, network
./install.sh --no-hook  # install everything EXCEPT the global git core.hooksPath change
./uninstall.sh        # remove the symlinks; restore *.maestro-bak backups + core.hooksPath
```

## Layout

| Path | What |
|---|---|
| `skills/` | agent skills + the `ensemble` CLI (`skills/ensemble/scripts/ensemble.sh`) — shared by both agents |
| `commands/` | Claude slash commands — one `.md` per command, all symlinked by `install.sh` |
| `bin/` | `board` CLI, `ensemble-tui` (terminal dashboard), `ensemble-web` (browser dashboard) — symlinked onto `PATH` |
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
