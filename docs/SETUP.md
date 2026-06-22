# Setting up maestro

This gets the Claude + Codex collaborative paradigm running on a fresh machine,
step by step. It works the same on Linux, macOS, and WSL2. Budget ~10 minutes.

If you just want the short version, the README quickstart has it. This guide
explains each step so you know what's happening and can fix it if something's off.

---

## 1. Prerequisites

You need five things on your `PATH`. Check what's missing:

```bash
for c in claude codex tmux python3 git; do printf '%-8s ' "$c"; command -v "$c" || echo MISSING; done
echo "PATH has ~/.local/bin: $(case ":$PATH:" in *":$HOME/.local/bin:"*) echo yes;; *) echo NO;; esac)"
```

| Tool | What it's for | If missing |
|---|---|---|
| `claude` | Claude Code CLI | https://claude.com/claude-code |
| `codex` | OpenAI Codex CLI | `npm i -g @openai/codex` (or your installer) |
| `tmux` | live side-by-side agent panes | `apt install tmux` / `brew install tmux` |
| `python3` | the dashboard TUI + build board (stdlib only) | usually preinstalled |
| `git` | everything | your package manager |

If `~/.local/bin` isn't on your `PATH`, add it to your shell rc and reopen the shell:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc   # or ~/.zshrc
```

Both CLIs must be signed in (`claude` once interactively; `codex` once). That's it
for prerequisites.

---

## 2. Install

```bash
git clone git@github.com:wdong97/maestro.git ~/maestro
cd ~/maestro
./install.sh
```

`install.sh` is idempotent and backs up anything it would overwrite to
`<file>.maestro-bak`. It wires up:

- **Skills** → symlinked into `~/.claude/skills/` and `~/.codex/skills/` (both agents
  see `ensemble`, `duel`, `spawn`, `delegate-*`, `board`).
- **Slash commands** → `~/.claude/commands/` (`/duel`, `/spawn`, `/ensemble-review`,
  `/ensemble-doctor`).
- **CLIs** → `~/.local/bin/ensemble`, `~/.local/bin/board`, `~/.local/bin/ensemble-tui`.
- **Coding guidelines** → `@import`ed into `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`.
- **Pre-push review hook** → global `core.hooksPath` so every repo gets it.

Because everything is a symlink into the repo, editing a file in `~/maestro`
takes effect immediately, and `git pull` updates the whole system.

---

## 3. Verify

```bash
ensemble doctor
```

Expect `0 fail`. It checks the CLIs, the skill/command/symlink wiring, the push
hook, the artifacts dir, and network reachability to both model APIs. Run it any
time something feels off — it's the fastest way to localize a problem.

One expected note: a `WARN` for "no tmux server running yet" is normal before your
first run.

---

## 4. When changes take effect

| You change… | Takes effect… |
|---|---|
| a CLI script (`ensemble`, `board`) or the push hook | immediately |
| a skill, slash command, or the coding guidelines | **next agent session** |
| add a *new* skill / command / bin file | re-run `./install.sh`, then next session |

So after installing, **start a fresh Claude or Codex session** to pick up the skills
and commands. (An already-open session won't see them.)

---

## 5. Your first runs

### Duel — both models, one answer
```bash
ensemble duel "What's the cleanest fix for <a real problem>?"
tmux attach -t duel-<name>     # watch both panes; Ctrl-b d to detach
```
When both finish, the orchestrating agent reads `~/.ensemble/duel/<name>/{claude,codex}.out`
and synthesizes. From inside Claude use `/duel`; from Codex use `$duel`.

### Delegate — hand work to the other model
From a Claude session running Fable: `delegate-fable` (keep planning, send the build
to Codex). From Opus: `delegate-opus`. From Codex: `delegate-codex` (send taste/UI
work to Claude). Effort scales to the task — trivial work doesn't pay for `xhigh`.

### Review on every push
Just push. The hook has the other agent review your diff and asks before it leaves:
```bash
git push                      # → peer review → "push anyway? [y/N]"
ENSEMBLE_REVIEW=0 git push    # skip it once
```

### Watch what's running
```bash
ensemble jobs                 # every run + status, from any terminal
ensemble tail last            # follow the most recent run live
ensemble dash                 # interactive dashboard — run in a REAL terminal (not an agent box)
```

### Track the work on a board
```bash
cd <your-project>
board init                    # scaffold orchestration/ (edit board-state.json: project + slices)
board serve                   # open the live Kanban + roadmap
board claim S1.api --owner you  →  board progress …  →  board review …  →  board done …
```

---

## 6. How agents use this (for Claude & Codex)

Agents don't need to be told the commands — the skills are auto-available and
description-triggered. As an agent working in any repo on this machine:

- The **coding guidelines** are already in your context (via the `@import`).
- To run a head-to-head, use the **`duel`** skill / `ensemble duel`. To delegate, use
  the matching **`delegate-*`** skill. To review a diff, **`ensemble review`**.
- To coordinate multi-agent work, use the **`board`** skill: `board claim` before you
  start, `board progress`/`block` as you go, `board review`→`done` with `board gate`
  evidence, and `board add ITER "…"` for unplanned work. Claim before starting so two
  agents don't collide.
- Treat the other agent's output as a suggestion until you verify it against the repo
  and tests. Read `*.out` (clean answers), not the full `*.log` streams.

Run `ensemble doctor` to confirm you can reach both APIs (a network FAIL from inside a
sandboxed Codex run means you need to escalate that run's permissions).

---

## 7. More machines

Same three commands per machine — the repo carries the whole system:

```bash
git clone git@github.com:wdong97/maestro.git ~/maestro
cd ~/maestro && ./install.sh && ensemble doctor
```

Pull updates anytime with `git pull` (symlinks mean no reinstall needed for edits;
re-run `./install.sh` only after adding brand-new skills/commands).

---

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| `ensemble: command not found` | `~/.local/bin` not on `PATH` — see step 1, reopen shell |
| Slash command / skill not showing | start a **new** agent session; for a brand-new one, re-run `./install.sh` |
| `ensemble dash` errors with `cbreak()` / curses | you're in an agent's command box or a pipe — run it in a real terminal, or use `ensemble jobs` |
| A delegation "hangs" forever | it's usually just `xhigh` being slow — `ensemble tail <name>` to confirm it's moving; lower `--eff` |
| Codex run can't reach the API | its sandbox blocked network — re-run with escalated permissions |
| dashboard / board page won't load | it must be *served*, not opened as a file — use `board serve` / the board's `serve.sh` |
| push isn't reviewed | confirm the hook: `git config --global core.hooksPath` should point at `~/.config/git/hooks` |

Still stuck? `ensemble doctor` first — it names the broken piece.
