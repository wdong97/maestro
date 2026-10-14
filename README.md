# maestro

Run a shop of coding-agent sessions from your terminal: you talk to one orchestrator per
machine, it hands work to implementer, reviewer, merger and researcher sessions, and every
handoff lands on a shared board with gates a human signs off. Claude Code and Codex, on one
machine or several. No daemon, no database: a registry of sessions, a messaging command, role
briefs, a board, and the skills that make each role behave.

Think of it as [Gas Town](https://github.com/steveyegge/gastown)'s roles and protocol at
[Claude Squad](https://github.com/smtg-ai/claude-squad) weight, over the terminals you
already have.

## The shop

```
you
└── orchestrator (one per machine)      maps, assigns, gates, reports; never implements
    ├── implementer                     one claimed card at a time, own worktree
    ├── reviewer                        independent, other model family for gate work
    ├── merger                          merge queue; only signed-off cards
    └── researcher                      answers questions, changes no code
```

| Layer | What does it | Status |
|---|---|---|
| Registry and messaging across machines | `cb register / who / send / board` | built |
| Role briefs per project | `board init` writes `orchestration/ROLES.md` | built |
| Shared board with gates and sign-off | `board claim / review / gate / signoff / done` | built |
| Function sessions on one machine | `ensemble spawn / delegate / duel / relay / review` | built |
| Status up the chain | `/metastatus`, `/recap`, `/standup`, `ensemble jobs / dash / web` | built |
| Review before every push by the other model | global `pre-push` hook | built |
| One orchestrator per machine | a session you register as `<machine>/orchestrator` | convention |
| A top orchestrator across machines | | next |

Cross-machine messaging reads and types into terminals through [Orca](https://orca.dev);
without it, `cb` works for the machine you are on.

## Quickstart

Needs `claude`, `codex`, `tmux`, `python3`, and `~/.local/bin` on your `PATH`.

```bash
git clone https://github.com/wdong97/maestro.git ~/maestro
cd ~/maestro && ./install.sh          # symlinks skills, commands, cb/ensemble/board; runs the doctor
```

Then, in a project:

```bash
board init                            # orchestration/: board, dashboard, ROLES.md
cb register wsl01/orchestrator --scope "maps and assigns work for this repo"
cb who                                # every registered session on every machine, live state
cb send wsl01/impl-auth "card S1.api is yours; files: api/auth.py, tests/test_auth.py"
board claim S1.api --owner wsl01/impl-auth
```

`cb send` never types over you. If the target's input box is empty, the message goes now.
If you have something typed there, it waits until you send yours, then follows in order.
`cb queue` shows what is waiting and why.

`cb` reads `~/.config/maestro/cb.json` for this machine's name, the registry directory
(a git checkout, if you want it shared), and the Orca environment name of each other
machine. Without the file it uses the hostname and a local registry.

The skills also install as a Claude Code plugin, without the symlinks:

```
/plugin marketplace add wdong97/maestro
/plugin install maestro@maestro
```

The plugin carries the skills and slash commands only. `cb`, `ensemble`, `board` and the
pre-push hook come from `./install.sh`.

## Everything else

[docs/TOUR.md](docs/TOUR.md) walks every command and skill: duel, delegate, spawn, relay,
jobs and dashboards, reap, the board, standup, plain-docs, eli5, recap, closeout,
next-steps, start-task, skill-audit, goal-loop. [docs/SETUP.md](docs/SETUP.md) covers each
install step and what to do when one fails.

## Verify / undo

```bash
ensemble doctor         # CLIs, skills, commands, helper bins, hook, platform, network
./install.sh --no-hook  # everything except the global git core.hooksPath change
./uninstall.sh          # remove the symlinks; restore *.maestro-bak backups + core.hooksPath
```

## Layout

| Path | What |
|---|---|
| `bin/` | `cb` (registry + messaging), `board` (project board CLI), `ensemble-tui`, `ensemble-web` |
| `skills/` | agent skills + the `ensemble` CLI (`skills/ensemble/scripts/ensemble.sh`), shared by both agents |
| `commands/` | Claude slash commands, one `.md` each |
| `board/` | what `board init` scaffolds: `status.py`, dashboard, `ROLES.md`; plus the `cb board` page |
| `hooks/pre-push` | peer-review-before-push gate |
| `guidelines/` | coding guidelines `@import`ed into every session |
| `.claude-plugin/` | plugin and marketplace manifests |

Runtime artifacts live in `~/.ensemble/`; per-project board state in that project's
`orchestration/`; the session registry wherever `cb.json` points.

## Where it sits

Local orchestrators in this space either manage worktree sessions with no roles or protocol
(Claude Squad, Conductor, Vibe Kanban, Crystal), run a daemon off an issue tracker for one
vendor (OpenAI's [Symphony](https://github.com/openai/symphony)), or bring a database and
their own vocabulary for 20 to 30 agents (Gas Town). maestro borrows their primitives: a
ledger as the control plane, hierarchical identity, implementer never reviews own work,
policy versioned in the repo. It keeps the weight at a few scripts over tmux and terminals.
