---
description: Explain the last thing that happened — or a thing you name — in plain words, with the decision it leaves you with
argument-hint: "[file | error | term | 'the last message']"
---

Apply the `eli5` skill to the request below. Read the skill first
(`~/.claude/skills/eli5/SKILL.md`), then follow it.

1. **No args** → explain your own previous message, or the task you just did. If it was
   long, explain the part the user has to act on.
2. **Args naming something** → explain that file, error, term, command, or design.
3. **Don't redo the work.** Facts, recommendation, and plan stay identical — this is a
   retelling. If the plain version exposes a mistake in the original, say so as its own
   sentence rather than silently correcting it.
4. **Keep it to roughly 150 words**, as chat prose: what it is, one everyday analogy and
   where it breaks, why it matters here, and their next decision (or "nothing to do").
   Note anything the simple version hides with "What I skipped: …".
5. **Don't strip precision they need.** If the subject is a spec, a security finding, or
   an incident, give the plain version first and offer the exact one.

Args: $ARGUMENTS
