---
name: delegate-fable
description: Cost-aware delegation with Fable 5 as orchestrator and Codex (gpt-5.5 / xhigh / fast) as the implementer. Use in a Claude Code session running Fable 5 when you want to keep planning, frontend, visual, and taste work in-session and dispatch backend/bulk/well-specced execution to Codex's free quota. See also delegate-opus (Opus orchestrator) and delegate-codex (inverted).
---

# delegate-fable — Fable 5 orchestrates, Codex implements

This is the canonical delegation pattern (the generic `delegate` skill, named for
its pairing). Orchestrator = **Fable 5** (this session): expensive, worth it for
planning, frontend, visual output, ideation, and taste. Implementer = **Codex
gpt-5.5 / xhigh / fast**: the user's Codex quota sits unused, so it's effectively
free heavy-execution capacity.

Confirm the session is on Fable 5 (`/model` shows it); if not, switch or use the
variant that matches your model.

## Routing

**Keep in this Fable session:** planning, architecture, task decomposition;
frontend / UI / layout / styling / anything visual; design, ideation, judgment
calls; and the gnarly bits (subtle logic, decisions Codex would get wrong).

**Dispatch to Codex:** backend implementation; large mechanical edits,
scaffolding, boilerplate; anything well-specified enough that execution — not
thinking — is the bottleneck.

Ask: *is the value in the ideas/visuals, or in the keystrokes?* Ideas/visuals
stay; keystrokes go to Codex.

## Dispatch (zombie-proof background launch)

Write a self-contained spec first (repo path, exact task, files, expected
behavior, constraints, definition of done). Then launch in the background
(`run_in_background: true`) so you keep working while Codex executes. `fast` must
be set explicitly (`fast_default_opt_out = true`). Rationale for each guard is in
the `delegate` skill.

```bash
SLUG=<short-kebab>; REPO=<repo>; PROMPT='<self-contained spec>'
DIR=~/.codex/dispatch && mkdir -p "$DIR"
LOG="$DIR/$SLUG.log"; OUT="$DIR/$SLUG.out"; DONE="$DIR/$SLUG.done"; rm -f "$DONE"; : >"$LOG"
( timeout -k 1m 30m codex exec -C "$REPO" --skip-git-repo-check \
    -m gpt-5.5 -c model_reasoning_effort='"xhigh"' -c service_tier='"fast"' \
    --sandbox workspace-write --full-auto \
    -o "$OUT" "$PROMPT" </dev/null >"$LOG" 2>&1 ; echo "$?" >"$DONE" ) &
CPID=$!; tail -n +1 --pid="$CPID" -f "$LOG"
echo "[delegate-fable] $SLUG done, codex exit=$(cat "$DONE")"
```

Use `--sandbox read-only` for analysis-only dispatches.

## Review

When done, read **`$OUT` only** (the short final message) — do NOT pull the full
`$LOG` stream back into this session unless debugging; that stream is the token
cost delegation avoids. `$DONE` is ground truth for completion (its contents =
codex exit code; `0` ok, `124` timeout). Verify Codex's work against the spec,
repo, and tests before trusting or committing. Fable owns final judgment.
