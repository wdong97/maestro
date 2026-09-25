---
description: Drive a long-lived dev agent hop by hop — draft the prompt, get your "go", send it, check the report against git
argument-hint: "[relay name, or what the dev agent should build next]"
---

Apply the `relay` skill (`~/.claude/skills/relay/SKILL.md`) to the relay or task in the
args.

1. If no relay exists yet, set one up: `ensemble relay new NAME --to codex|claude --dir D`.
2. Draft the next hop's prompt and show it. Stop for "go" — every hop.
3. `ensemble relay send NAME <file>`, then `ensemble relay wait NAME` in the background.
4. Check the RELAY-REPORT against git (commit exists, pushed if claimed), tell the user
   what happened in plain words, and show the next draft.
5. Stop on `blocked` or `needs-input`. Push and eval hops are approved by name.

Args: $ARGUMENTS
