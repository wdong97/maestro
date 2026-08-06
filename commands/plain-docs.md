---
description: Draft or revise a document in plain, user-friendly language (README, guide, release note, proposal, runbook)
argument-hint: "<file path to revise | what to draft> [--check]"
---

Apply the `plain-docs` skill to the request below. Read the skill first
(`~/.claude/skills/plain-docs/SKILL.md`), then follow it.

1. **Pick the mode from the args.**
   - Args name an existing file → **revise** it. Read it in full first.
   - Args describe something to write → **draft** it. Ask where it should live if
     that isn't obvious.
   - Args end with `--check` → **review only**: report what's wrong against the
     skill's ship checklist, change nothing.
2. **Do Step 0 before writing.** Reader, their task, the one sentence that matters.
   If the material doesn't answer those, ask — don't invent product facts, limits,
   dates, or guarantees. Unknowns become `TODO: confirm …`.
3. **Match the surroundings.** Check for a `STYLE.md`, `CONTRIBUTING.md`, or docs
   config in the repo and follow it over the skill's defaults; match the formatting of
   neighboring documents.
4. **When revising, preserve the author's voice and every factual claim.** Fix what
   blocks the reader. If a sentence looks wrong rather than unclear, flag it instead of
   rewriting it.
5. **Report back**: the 3–5 changes that mattered most and why, plus any `TODO`s left
   for the author. Don't paste the whole document back if you edited it in place.

Args: $ARGUMENTS
