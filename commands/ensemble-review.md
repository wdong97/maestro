---
description: Peer-review the current git diff with the other agent (Codex by default)
argument-hint: "[--base REF | --commit SHA | --uncommitted] [--by claude|codex|both]"
---

Peer-review the current changes with the other agent via the `ensemble` skill/CLI.

1. Run: `ensemble review $ARGUMENTS`
   (no args = uncommitted vs HEAD, reviewer = codex; `--by both` runs both agents;
   `--base origin/main` reviews the outgoing branch diff.)
2. Summarize the findings for the user, ranked by severity with file:line refs,
   clearly separating confirmed bugs from suggestions.
3. Verify any non-trivial finding against the actual code before acting on it —
   the review is input, not a verdict. Offer to fix the confirmed issues.

Note: this is the same review the pre-push hook runs automatically on every push.
