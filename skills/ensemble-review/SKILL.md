---
name: ensemble-review
description: Peer-review the current git diff with the OTHER coding agent (Claude from a Codex session, Codex from a Claude session). Use when the user wants an independent cross-agent code review of pending changes, before committing or pushing.
---

# ensemble-review — cross-agent diff review

Drive the `ensemble` CLI (`ensemble` is on PATH; see the `ensemble` skill for docs).
From a Codex session the natural reviewer is Claude.

1. Run: `ensemble review --by claude [--base REF | --commit SHA | --uncommitted]`
   - no selector = uncommitted vs HEAD
   - `--base origin/main` = review the outgoing branch diff
   - `--by both` = both agents review
   Reviewing with claude needs network — escalate if the sandbox blocks it.
2. Summarize findings ranked by severity with file:line refs, separating
   confirmed bugs from suggestions.
3. Verify any non-trivial finding against the actual code before acting. Offer to
   fix the confirmed issues.

Note: the pre-push hook already runs this automatically on every push (default
reviewer codex; set `ENSEMBLE_REVIEWER=claude` to flip it).
