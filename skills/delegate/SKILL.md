---
name: delegate
description: Cost-aware, model-agnostic delegation. You (the orchestrator — whatever model your current session runs) keep planning, taste, and the hardest logic; you hand mechanical or bulk work to an implementer model you choose with `--to`. Use when deciding who does a task, or before backend/heavy/boilerplate work that should be specced and dispatched to save the orchestrator's tokens.
---

# delegate — orchestrator model + implementer model, your choice

One command, any models. The **orchestrator** is your current session (set its model
with `/model`, or just be in whichever agent you're in). The **implementer** is the
model you delegate to with `--to`; `ensemble delegate` auto-routes to the Codex or
Claude CLI by model name.

```bash
ensemble delegate --to <model> [--from <model>] [--eff low|medium|high|xhigh] [--ro] "<spec>"
```

- `--to` (required): `opus` · `fable` · `sonnet` · `haiku` · `codex` · `gpt-5.5`, or any
  full id (`claude-opus-4-8`, `gpt-5.5`, …). Claude-family → `claude -p`; GPT/Codex
  family → `codex exec`.
- `--from` (optional): label your orchestrator model (documentation only — the
  orchestrator is always your current session).
- `--eff` (Codex implementers): scale reasoning to the task — `low` trivial · `medium`
  routine · `high` standard · `xhigh` gnarly. Pick the lowest that will work.
- `--ro`: read-only (analysis, no edits). Default lets the implementer edit the repo.

It runs in the **background** (zombie-proof) and writes to `~/.ensemble/dispatch/`, so it
shows in `ensemble jobs` and you can `ensemble tail <name>` it. Run the command itself in
the background so you keep working while the implementer runs.

## What to keep vs delegate

**Keep with the orchestrator (your session):** planning, architecture, decomposition;
design, taste, and visual judgment; the gnarly, subtle, correctness-critical logic.

**Delegate to the implementer:** backend/CRUD, scaffolding, boilerplate, large
mechanical edits — anything where the spec fully determines the output and execution,
not thinking, is the bottleneck.

Ask: *is the value in the ideas/judgment, or in the keystrokes?* Ideas stay; keystrokes
go. **Choose the implementer by cost and fit:** send bulk to the model whose capacity is
cheap/idle; reserve premium models (and your own session) for work that needs them.

## Patterns

```bash
# Premium Claude session → send the build to Codex (its quota is the cheap capacity):
ensemble delegate --to codex --eff high "Implement the /healthz endpoint per <spec>; keep tests green."

# Codex session → send the part that needs Claude's taste/UI to Claude:
ensemble delegate --to opus "Polish the dashboard layout for <screen>; match existing styles."
#   (spawning Claude needs network; if your Codex sandbox blocks it, run with escalated permissions.)

# Read-only analysis instead of edits:
ensemble delegate --to gpt-5.5 --ro "Audit src/auth for missing input validation; list findings."
```

## Review the result

Read the **clean answer** (`~/.ensemble/dispatch/<name>.out`), not the full stream, unless
debugging — that stream is the token cost delegation avoids. The `.done` file holds the
implementer's exit code (`0` ok, `124` timeout). Verify the implementer's work against the
spec, repo, and tests before trusting or committing it. The orchestrator owns final judgment.
