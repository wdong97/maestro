---
name: delegate-codex
description: Inverted cost-aware delegation with Codex (gpt-5.5 / xhigh) as orchestrator and the best available Claude model (Opus 4.8, or Fable 5) as the implementer. Use in a Codex session when a task needs Claude's taste, frontend/visual output, or hardest-case reasoning — dispatch just those parts to Claude and keep everything else in Codex's free quota.
---

# delegate-codex — Codex orchestrates, Claude implements

Inverts the usual cost model. Orchestrator = **Codex gpt-5.5 / xhigh** (this
session): effectively free quota, so it does the bulk of the work. Implementer =
**best Claude model** — default **Opus 4.8** (`claude-opus-4-8`), or **Fable 5**
(`claude-fable-5`) when the task is visual/ideation/taste-heavy. Here **Claude
tokens are the scarce, premium resource**, so spend them only where they clearly
pay off.

## Routing (spend Claude tokens sparingly)

**Keep in this Codex session:** planning, decomposition, backend implementation,
bulk/mechanical edits, scaffolding, refactors, tests — Codex is strong and free,
so default to doing it here.

**Dispatch to Claude only for high-value judgment:** frontend / UI / layout /
visual polish; design and ideation where taste matters; the single hardest,
most-subtle reasoning or correctness-critical piece where Opus's quality is worth
the spend. Pick Fable 5 for visual/ideation, Opus 4.8 for hard logic/coding.

Ask: *would this be meaningfully better in Claude's hands, and is it worth the
premium tokens?* If not, keep it in Codex.

## Dispatch (zombie-proof background launch)

Write a self-contained spec first. **Network caveat:** spawning `claude` needs
network; if this Codex session runs in a sandbox with network disabled, run the
command with escalated / full access (or the claude process can't reach its API).
Launch in the background so Codex keeps working.

```bash
SLUG=<short-kebab>; REPO=<repo>; MODEL=claude-opus-4-8   # or claude-fable-5
PROMPT='<self-contained spec>'
DIR=~/.codex/dispatch && mkdir -p "$DIR"
OUT="$DIR/$SLUG.out"; ERR="$DIR/$SLUG.err"; DONE="$DIR/$SLUG.done"; rm -f "$DONE"; : >"$OUT"
( cd "$REPO" && timeout -k 1m 30m claude -p "$PROMPT" \
    --model "$MODEL" --permission-mode bypassPermissions --output-format text \
    </dev/null >"$OUT" 2>"$ERR" ; echo "$?" >"$DONE" ) &
CPID=$!; tail -n +1 --pid="$CPID" -f "$OUT"
echo "[delegate-codex] $SLUG done, claude exit=$(cat "$DONE")"
```

Use `--permission-mode plan` instead of `bypassPermissions` for read-only
analysis (no edits).

## Review

`$OUT` holds Claude's final text; `$DONE` = claude exit code (ground truth; `0`
ok, `124` timeout, else failure — check `$ERR`). Verify Claude's edits against the
spec, repo, and tests before trusting or committing. Codex owns final judgment.
