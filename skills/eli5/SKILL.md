---
name: eli5
description: Re-explain the last thing that happened — your previous message, the current task, a diff, a command, an error, a file, or a term — in plain words a non-expert can follow, with one everyday analogy and the decision it leaves them with. Use when the user says "eli5", "explain like I'm five", "in plain English", "dumb it down", "I don't follow", "what does that actually mean", or asks what something they just saw really does.
---

# eli5 — explain it in plain words

Someone needs to understand what just happened well enough to decide what to do next.
They don't need the mechanism, the history, or your reasoning. Give them the shortest
true version.

## What to explain

- **No arguments** → the last thing you output: your previous message, the plan you
  proposed, the diff you made, the command you ran, the error that came back. If it was
  long, explain the part the reader has to act on, not all of it.
- **Arguments naming something** → explain that: a file, a function, an error string, a
  term, a tool, a design.

**This is a retelling, not a redo.** The facts, the recommendation, and the plan stay
exactly what they were. If explaining it plainly makes it obvious the original was
wrong, say that as its own sentence — don't quietly fix it inside the simpler version.

## Shape

Four short parts, about 150 words total. Skip any that don't apply. Three sentences is
a fine answer.

1. **What it is, in one sentence.** No preamble, no "so basically."
2. **One analogy from everyday life** — mail, keys, a kitchen, a queue at a counter, a
   shared shelf. Add the clause where it stops being true.
3. **Why it matters here** — what's different now for this person, this repo, this run.
4. **Your call** — the decision in front of them, or "nothing to do."

Write it as chat prose, not a document: no headings, no nested bullets. This is
something a person reads once and understands.

## Rules

- **Simplify the explanation, never the facts.** Nothing false to make it easy. Real
  paths, real names, real numbers — they still have to act on this.
- **One analogy, only if it earns its place.** A misleading analogy costs more than no
  analogy, and every analogy breaks somewhere. Say where.
- **Say what you left out** when the simple version hides something that could bite:
  one line, "What I skipped: …"
- **No new jargon.** If a term is unavoidable — it's in the error, or they'll need it to
  search — give it once with a plain gloss: **idempotent** (running it twice does the
  same thing as running it once).
- **Concrete nouns and events.** "The file gets read on startup," not "the read path is
  exercised during initialization."
- **Keep their words.** If they call it "the runner" or "the board," it stays that. Don't
  rename things mid-explanation.
- **Don't talk down.** Five is a register, not an estimate of the reader. No baby voice,
  no exclamation marks, no "great question," no apology for the earlier explanation.
- **If they're still lost, change the analogy — don't repeat it louder.** A second
  attempt from a different angle beats the same one with more words.

## Two things this isn't

If they need precision — a spec, a security finding, an incident timeline — don't strip
it. Give the plain version first, then offer the exact one.

For a **document** that has to read this way permanently, use the `plain-docs` skill.
`eli5` is a live answer in a conversation; `plain-docs` writes the file.

## Examples

**A rebase.**

> Technical: Rebased your branch onto `main` and force-pushed with `--force-with-lease`;
> the three fixup commits are squashed into `a1b2c3d`.
>
> eli5: Your work now sits on top of the team's newest code instead of the older copy you
> started from, and your three small "oops" commits are folded into one. The `--lease`
> part is a safety catch — if a teammate had pushed to this same branch while I worked,
> the push would have been refused instead of erasing their work. Nothing of yours was
> lost. Your call: nothing, unless someone else has this branch checked out — they'll
> need to re-pull it, because its history changed shape.

**An out-of-memory kill.**

> Technical: The pod OOM-killed at 512Mi; the sidecar shares the app's memory limit.
>
> eli5: The app and its helper process share one 512 MB shelf. The helper grew, the app
> no longer fit, and the system shut the whole thing down rather than let it take more.
> It's like two people sharing one carry-on — it doesn't matter whose stuff is whose,
> the lid still won't close. This will happen again at the same traffic level. Your call:
> give them separate limits, or raise the shared one. What I skipped: which of the two
> actually grew — the logs will say, and that changes which fix is right.
