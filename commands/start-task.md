---
description: Run intake on a new task — frame, explore, ask, plan — then stop and wait for your "go" before writing anything
argument-hint: "[the task — defaults to the latest request]"
---

Apply the `start-task` skill (`~/.claude/skills/start-task/SKILL.md`) to the task in the
args, or to the latest request.

1. **Frame** — restate the ask in 1–2 sentences: what gets delivered, where it's checked
   in the running system, and what's out of scope.
2. **Explore** — find where the work lands, what exists, overlap with other sessions
   and board cards, and relevant rules in CLAUDE.md/AGENTS.md and memory. 3+ file reads
   go to subagents.
3. **Ask** — every real fork in one batch, recommended option first, in plain words. Or
   say "No questions — no genuine forks."
4. **Plan** — numbered steps each with its check, expected complexities, one-line
   routing. Copy it into your in-session todo list (not a repo file — no approval needed).
5. **Gate** — stop and wait for "go." Only writes in the plan are approved.

Args: $ARGUMENTS
