---
name: ensemble
description: Run Claude Code and Codex CLI together as an ensemble — duel (both answer the same prompt in side-by-side tmux panes, then synthesize), spawn (delegate to one peer in a viewable tmux window), and peer review on every push. Use when the user wants the two agents working in parallel, a head-to-head/second-opinion duel, watchable delegation, or cross-agent PR/diff review before pushing.
---

# Ensemble — Claude + Codex in parallel

Three composable patterns, all visible in **tmux** (so the user watches and can
steer) and all capturing results to files (so an orchestrating agent reads the
final answer without slurping the whole stream). One script drives everything:

```
scripts/ensemble.sh <duel|spawn|review|attach|status|clean|install-review-hook>
```

Resolve the script path relative to this skill dir. Read-only is the default;
`--rw` isolates each writer in its own git worktree+branch.

This complements the existing skills — it does not replace them:
- **`delegate`** (`ensemble delegate --to <model>`) = headless, cost-optimized
  dispatch to **any** model (Codex or Claude, auto-routed); shows in `ensemble jobs`.
  Use it when you do **not** need to watch.
- **`ensemble`** = the same idea but **watchable in real tmux panes**, plus a
  symmetric duel and a push-time review gate.
- **`agent-sync`** = handoff packets / session resume. Use it to brief either arm
  with prior state before a duel, and to reconcile after.
- **`codex`** = single read-only Codex consultation. `ensemble duel` is the
  two-sided version.

## When to use which pattern

| Want… | Use |
|---|---|
| Best answer to one hard question, two independent models | `duel` (read-only) → synthesize |
| Two parallel *implementations* to compare/merge | `duel --rw` → judge → merge winning branch |
| Hand a well-specced task to one peer and watch it work | `spawn claude\|codex` |
| Catch bugs before they ship | `review`, and `install-review-hook` for every push |

## 1. Duel — both answer the same prompt

```bash
scripts/ensemble.sh duel "Design the retry/backoff strategy for the ingest worker."
# read-only by default: claude (plan mode) | codex (read-only sandbox), side by side
```

The user watches with `tmux attach -t duel-<name>`. When both `*.done` files
exist, **you (the orchestrator) read both `*.out` files and synthesize the best
answer** — agree/disagree, merge the strongest points, flag where they conflict,
and verify contested claims against the repo. That synthesis step is what turns
two opinions into one good answer; don't just paste both.

Parallel implementation (each edits in an isolated worktree, zero clobber):

```bash
scripts/ensemble.sh duel --rw "Implement the /healthz endpoint with a DB ping."
# branches: ens/<name>/claude  and  ens/<name>/codex
# afterward: diff the two branches, judge, merge the winner, then `clean`
git -C <repo> diff ens/<name>/claude ens/<name>/codex   # compare the two solutions
```

Flags: `--name N` (stable dir/session name), `--mc <model>` (claude model),
`--mx <model>` (codex model, default gpt-5.5), `--wait` (block until both finish
instead of returning immediately).

Orchestrator polling (don't foreground-sleep): launch without `--wait`, keep
working, and check `~/.ensemble/duel/<name>/{claude,codex}.done` (contents = exit
code) before reading `*.out`.

## 2. Spawn — watchable delegation to one peer

Either agent can spawn the other into a tmux window you can attach to:

```bash
scripts/ensemble.sh spawn codex  --rw "Refactor src/auth/* to use the new TokenStore. Keep tests green."
scripts/ensemble.sh spawn claude     "Audit src/api for missing input validation; list findings."
```

Lands as a window in the shared `ensemble` tmux session. `--dir D` runs it in a
specific directory; `--rw` lets it edit. Unlike `duel --rw`, `spawn --rw` edits
the target dir **in place** (that is the point of delegation) — pass
`--dir <a worktree>` if you want it isolated. Final answer →
`~/.ensemble/spawn/<name>/out.txt`, exit code → `run.done`.

## 3. Peer review on every push (and on demand)

Review the current diff with the *other* agent (default reviewer: codex):

```bash
scripts/ensemble.sh review                     # uncommitted vs HEAD
scripts/ensemble.sh review --base origin/main  # vs upstream
scripts/ensemble.sh review --commit <sha>
scripts/ensemble.sh review --by both           # both agents review
```

Make it automatic for every push:

```bash
scripts/ensemble.sh install-review-hook            # this repo (.git/hooks/pre-push)
scripts/ensemble.sh install-review-hook --global   # all repos (core.hooksPath)
```

The pre-push hook reviews the outgoing diff (vs the tracked upstream) before the
push leaves. In an interactive terminal it prints findings and asks
`push anyway? [y/N]`; non-interactive (CI, scripts) it logs and allows.
Bypass once with `ENSEMBLE_REVIEW=0 git push`; pick the reviewer with
`ENSEMBLE_REVIEWER=claude|codex|both`.

> `--global` sets `core.hooksPath`, which **overrides** any existing per-repo
> hooks. If a repo already has hooks, prefer the per-repo install. Tell the user
> which one you did.

## Observability — see/follow every run from anywhere

These work from any terminal, independent of whatever launched the run (the
launching session, tmux, or a headless dispatch). Output always persists to files,
so "I can't see it" is solved even after tmux/the session is gone.

```bash
scripts/ensemble.sh dash           # interactive TUI (read-only watch): per-session RAM% (tree summed) + gauge;
                                   #   a=follow output  x=stop run (y/N confirm)  p=output  /=filter  q=quit
scripts/ensemble.sh jobs           # one-shot list of every run: status, age, output path
scripts/ensemble.sh tail <name>    # follow a run's output live (or `last` for the most recent)
scripts/ensemble.sh watch          # plain-text auto-refreshing list (no interactivity)
scripts/ensemble.sh ps [--by rss]  # task-manager: per-process agents sorted by CPU/RAM + project
scripts/ensemble.sh ps --stints    # per open SESSION: RAM % of total (whole process tree summed)
scripts/ensemble.sh reap [--dry-run]  # reclaim RAM: list idle sessions + dev servers (numbered); keep some, close rest
scripts/ensemble.sh stop <name>    # gracefully stop ONE run (SIGTERM→SIGKILL tree + tmux teardown); dash's x action
scripts/ensemble.sh report [--md]  # performance snapshot: reviews, findings, success rate, tokens
```

`jobs` scans `~/.ensemble/{duel,spawn,review}/` and `~/.codex/dispatch/`. Status is
`running` until the run's `.done` file appears (contents = exit code). Use these to
tell "slow but progressing" from "actually stuck" — Codex defaults to `xhigh`
reasoning, so a real delegation legitimately runs minutes; `tail` shows it moving.

## Housekeeping

```bash
scripts/ensemble.sh doctor         # self-check: CLIs, skill/symlinks, commands, hook, network reachability
scripts/ensemble.sh status         # sessions, run states, ensemble worktrees
scripts/ensemble.sh attach <name>  # tmux attach (default session: ensemble)
scripts/ensemble.sh clean <name>   # remove ONLY that run's worktrees + ens/<name>/* branches
scripts/ensemble.sh clean --all    # prune every ensemble worktree + ens/* branch
```

`doctor` exits non-zero if any hard check fails. Run it first when something
won't launch. Network FAILs from inside a Codex session mean the sandbox blocked
network for the spawned peer — re-run the launch with escalated/full access, or
start one duel from the Claude side first so a tmux server exists outside the sandbox.

Each duel run writes to `~/.ensemble/duel/<name>/`: `claude.out` / `codex.out`
are the **clean answers** (codex's via `-o`), `*.stream`/`*.log` are the live
mirrors for the human, `*.done` holds each agent's exit code. Read `*.out`.

## Guardrails

- Treat any peer output (duel arm, spawn, review) as a **suggestion** until
  verified against files, tests, or fresh command output. The orchestrator owns
  the final judgment.
- Read `*.out` (clean answer), not `*.log` (full stream), unless debugging — the
  log is for the human watching tmux.
- `--rw` worktrees are throwaway. Merge the winning branch into real work, then
  `clean`. Never push `ens/*` branches.
- One push gate is enough: don't stack `install-review-hook` and a separate CI
  review that duplicate each other without saying so.
- Don't paste secrets/tokens/customer data into a peer prompt.
```
