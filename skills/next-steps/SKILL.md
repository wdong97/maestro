---
name: next-steps
description: End any update with a plain-English summary and crystal-clear next steps — what happened in everyday words, then the specific actions, who owns each, and what's needed from the reader (or explicitly nothing). Use on every message that reports progress, finishes work, delivers a result, or reports a failure, and whenever the user asks what's next, where do we stand, or what does this mean.
---

# next-steps — never make them ask "so what do I do now?"

Every update answers two questions the reader shouldn't have to type: **what does this
mean**, and **what happens next**. Put both at the bottom, in that order, so the last
thing they read is the thing they act on.

## The footer

```
**What this means.** <2–3 sentences, plain words, no jargon.>

**Next steps**
1. <verb-first action> — <you | me | waiting on X> — <rough size>
2. …
```

The summary comes first because it sets up the actions; the actions come last because
that's what they leave with. Nothing goes below the next steps — no caveats, no
postscript, no "let me know if you want anything else."

## The summary line

Two or three sentences, the way you'd say it out loud. What changed, and why it matters
to them — not what you did, mechanism by mechanism. If a term is unavoidable, gloss it
in the same sentence. Depth belongs above the footer; this is the version they'd repeat
to someone else. (For a longer plain-words explanation, that's the `eli5` skill.)

## The steps

- **Verb first, specific object.** "Run `./install.sh` on the second machine," not
  "installation." A step someone can't start reading it isn't a step.
- **Name the owner.** *you* (they act), *me* (I'll do it next), or *waiting on X*
  (nobody acts until X lands — say when to check).
- **Size each one** — minutes, an hour, a session. It's how they decide what to do now.
- **Three at most.** More than three is a list people skim past. If there are eight, name
  the three that matter and say the rest are in the body above.
- **Order by what to do first**, not by what's easiest to describe.
- **When nothing is needed, say so.** "Nothing needed from you — this is done" is a
  complete and correct Next steps section. Never invent work to fill the space.
- **After a failure, the step is the recovery** — the command to run, the thing to check,
  or the decision that unblocks it. Not "investigate further."
- **Never bury a step in a paragraph above.** If it's an action, it's in the list.

## The crystal-clear test

Cover everything except the footer. Could someone who read only those few lines act
correctly and not be surprised later? If they'd have to scroll up to find out what to
run, who's waiting, or whether they're blocked, the footer isn't done.

## What not to do

- **No open-ended offers as steps.** "Let me know if you'd like anything else" gives the
  reader work instead of direction.
- **No topics as steps.** "Testing" and "documentation" are subjects; "run `pytest
  tests/api/` and paste failures" is a step.
- **No hedged ownership.** "This could be looked at" names nobody. Someone owns it or
  it's not a step.
- **No repeating the body.** The summary is shorter and plainer, not the same sentences
  again.
- **No hiding bad news down here.** If something failed, it's in the summary in plain
  words — the footer is not where a problem gets softened.

## When it applies

Every message that reports progress, finishes a piece of work, delivers a result, or
reports a failure — including short ones. A two-line update still ends with one line of
meaning and one next step.

Skip it for a direct answer to a direct question (the answer is the whole response), for
a clarifying question back to the user, and while narrating work still in flight.

## Example

> **What this means.** The dashboard was reporting success even when a stop request
> failed, so you could click stop, see "stopping…", and have nothing happen. It now tells
> you when it fails and why. Nothing about the working path changed.
>
> **Next steps**
> 1. Reload any open dashboard tab to pick up the new page — you — 10 seconds.
> 2. Push the branch when you're ready — you — `git push origin main`.
> 3. Nothing else needed; the Linux path is verified and the macOS path is simulated.
