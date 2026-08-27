---
description: Audit what's left in this thread, report it in plain English, finish only what you approve, then stop
argument-hint: "[extra scope to include, e.g. 'and the board changes']"
---

Apply the `closeout` skill to this session. Read the skill first
(`~/.claude/skills/closeout/SKILL.md`), then follow its phases in order.

1. **Name the goal** this session set out to reach — one sentence in the user's own
   terms, taken from their opening request, plus the pivot if it moved. Then **audit**
   every item in this thread's scope — what the user asked for (including
   requests a later pivot replaced), what you promised and never did, and what is
   actually on disk. Verify with `git status`, `git diff --stat`, the files, and the
   test output. Your earlier messages don't count as evidence.
2. **Report** in plain English, leading with the goal and how far it got — met /
   mostly met / partly met / not met / changed midway, judged from the Done list rather
   than from effort spent — then Done (with proof), Left (with a size), Not doing, Needs
   you. Say plainly if something failed or if tests never ran.
3. **Ask one question** — which leftovers to finish now, with your recommendation. If
   nothing is left, skip it. Start nothing while the question is open.
4. **Finish only what they approve**, smallest change each, verifying as you go. Report
   any bug you find instead of fixing it.
5. **Close**: state of the work, what's uncommitted plus the command to finish it,
   follow-ups they can paste into an issue. Then stop — no new suggestions.

Anything in the args is extra scope to include in the audit.

Args: $ARGUMENTS
