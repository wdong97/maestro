---
name: delegate-opus
description: Cost-aware delegation with Claude Opus 4.8 as orchestrator and Codex (gpt-5.5 / xhigh / fast) as the implementer. Use in a Claude Code session running Opus 4.8. Because Opus is itself a top-tier coder, the bar to delegate is higher than delegate-fable — keep architecture and all correctness-critical logic in-session, dispatch only mechanical/bulk/well-specced work to Codex.
---

# delegate-opus — Opus 4.8 orchestrates, Codex implements

Orchestrator = **Opus 4.8** (this session): premium, and unlike a pure
planning model it is one of the strongest implementers available — so it earns
its tokens on hard *coding*, not just planning. Implementer = **Codex gpt-5.5 /
xhigh / fast**: free heavy-execution capacity.

Confirm the session is on Opus 4.8 (`/model`). If you're on Fable, use
`delegate-fable` instead (different routing bar).

## Routing (higher bar to delegate than the Fable variant)

**Keep in this Opus session:** architecture and decomposition; **all gnarly,
subtle, or correctness-critical logic** — Opus is better than Codex here and the
cost is justified; anything where a wrong implementation is expensive to catch;
plus design/judgment calls.

**Dispatch to Codex only when execution is genuinely mechanical:** boilerplate,
scaffolding, large repetitive edits, well-specified backend CRUD, test
fixtures — work where the spec fully determines the output and Opus would just be
typing. If you'd have to think hard while writing it, keep it.

Rule of thumb: Fable delegates *implementation*; Opus delegates *only typing*.

## Dispatch (zombie-proof background launch)

Spec it fully, launch in the background (`run_in_background: true`), `fast` set
explicitly. Full rationale in the `delegate` skill.

```bash
SLUG=<short-kebab>; REPO=<repo>; PROMPT='<self-contained spec>'
DIR=~/.codex/dispatch && mkdir -p "$DIR"
LOG="$DIR/$SLUG.log"; OUT="$DIR/$SLUG.out"; DONE="$DIR/$SLUG.done"; rm -f "$DONE"; : >"$LOG"
( timeout -k 1m 30m codex exec -C "$REPO" --skip-git-repo-check \
    -m gpt-5.5 -c model_reasoning_effort='"xhigh"' -c service_tier='"fast"' \
    --sandbox workspace-write --full-auto \
    -o "$OUT" "$PROMPT" </dev/null >"$LOG" 2>&1 ; echo "$?" >"$DONE" ) &
CPID=$!; tail -n +1 --pid="$CPID" -f "$LOG"
echo "[delegate-opus] $SLUG done, codex exit=$(cat "$DONE")"
```

Use `--sandbox read-only` for analysis-only dispatches.

## Review

Read **`$OUT` only**; `$DONE` = codex exit code (ground truth). Because you
delegated only mechanical work, review is cheap — but still verify against the
spec and tests before committing. Opus owns final judgment.
