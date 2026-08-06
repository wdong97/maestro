---
name: plain-docs
description: Draft or revise a document in plain, user-friendly language — README, setup or how-to guide, help article, release note, proposal/RFC, runbook, internal memo, announcement. Use when writing a document a person will read, when asked to make a draft clearer, simpler, friendlier, shorter, or less corporate, or when reviewing a draft before it goes to users, customers, or teammates. Not for code, code comments, or generated API reference unless the prose around them is the problem.
---

# plain-docs — write documents people can actually use

A document works when the reader finishes their task. Everything below serves that.
Team-neutral by design: no house voice, no product assumptions. If your team has a
style guide, it wins — treat this as the floor, not the ceiling.

**Is this the right skill?** If the document's job is to make someone believe, want, or
buy — a landing page, sales email, launch announcement — that's persuasion, and a
copywriting skill fits better. Stay here when the job is to help someone finish a task
or make a decision.

## Two modes

**Draft** — you're writing something new. Do Step 0, pick a skeleton, write, then run
the ship checklist.

**Revise** — someone already wrote it. Keep their voice and their meaning. Fix what
blocks the reader: buried answer, vague steps, jargon, filler. Then tell the author the
3–5 changes that mattered most, so the next draft needs less work. Never change a
factual claim to make a sentence flow — flag it instead.

## Step 0 — answer three questions before writing a word

1. **Who reads this, and what do they already know?** A new customer, an on-call
   engineer at 3am, and an exec skimming on a phone need three different documents.
2. **What do they need to do or decide when they're done?**
3. **What one sentence must they remember if they read nothing else?**

If the source material doesn't answer these, ask the user. Do not invent product
facts, limits, prices, dates, or guarantees to fill a gap — write `TODO: confirm …`
and keep going.

## Shape: answer first

Readers skim, then commit. Earn the commit in the first three lines.

- **Title = the job, not the category.** "Connect your calendar" beats "Calendar
  Integration Overview."
- **Open with what this is, who it's for, and the action.** Background, history, and
  rationale go last or behind a link.
- **Headings are tasks or answers**, so the table of contents reads like a menu:
  "Reset a password," not "Password Management."
- **One idea per paragraph**, four sentences or fewer. If a paragraph has steps in it,
  it's a list.
- **Steps are numbered, each with a verifiable end state** — the reader must be able to
  tell whether step 3 worked before starting step 4.
- **Front-load each sentence** with its subject and verb. Conditions come after the
  instruction: "Select Save, then close the tab" — not "After you have selected Save,
  and assuming the tab is still open, …"

> Before: This document provides an overview of the authentication subsystem and
> outlines the various configuration options available to administrators.
>
> After: Set up sign-in for your team. You'll register the app, connect your identity
> provider, and test one login — about 10 minutes.

## Sentences: plain, concrete, addressed to a person

- **Talk to the reader as "you."** The product or team is "we" or its name. Both in
  the same sentence is fine: "We email the invite; you approve it."
- **Active voice with a named actor.** Passive hides who acts, and the reader usually
  needs to know whether it's them.
- **Concrete beats abstract; numbers beat adjectives.**
- **Verbs, not noun-clumps.** "Configure the webhook," not "perform webhook
  configuration."
- **One term per concept.** Pick "workspace" or "org," never both. Synonyms read as
  elegance to the writer and as two features to the reader.
- **Define jargon on first use, or cut it.** An acronym earns its place only if it
  appears three or more times.
- **Say what to do.** Prohibitions leave the reader without a next step: "Use a token
  with `read:pkg`" beats "Don't use an unscoped token."
- **Cut hedges and intensifiers**: very, quite, really, actually, basically,
  essentially, fairly, somewhat. They add length and subtract confidence.

> Before: The invitation will be sent once the account has been provisioned.
>
> After: We email the invite as soon as the account is ready — usually under a minute.

> Before: Performance has been significantly improved in this release.
>
> After: Search now returns in about 200 ms, down from 1.4 s.

## When something goes wrong

Failure messages, troubleshooting sections, and known-issue notes all follow the same
order: **what happened → why, if you know → what to do next.** No blame, no cuteness,
no "unexpected error." The reader is already frustrated; give them the next action.

> Before: An unexpected error occurred. Please try again later.
>
> After: We couldn't save your changes — the connection dropped. Your draft is safe
> locally. Reconnect and select Save again; if it fails twice, send us the log at
> `~/.app/logs/latest.log`.

## Words to swap

| Instead of | Write |
|---|---|
| utilize, leverage | use |
| in order to | to |
| prior to / subsequent to | before / after |
| due to the fact that | because |
| in the event that | if |
| at this point in time | now |
| facilitate, enable (as a verb for help) | help, let |
| commence / terminate | start / stop |
| a number of | some, or the actual number |
| is able to | can |
| please be advised that | (delete) |
| it is recommended that you | we recommend, or just the instruction |
| functionality | features, or what it actually does |
| robust, seamless, powerful, best-in-class | the specific behavior or number |

## Avoid — reader-shaming, filler, and AI tells

- **"Simply," "just," "easy," "obviously," "of course."** When it doesn't work, these
  tell the reader the failure is their fault. Delete them; the instruction survives.
- **Puffery with no content**: cutting-edge, game-changing, revolutionary, world-class,
  next-generation. Replace with a measurement or cut.
- **Openers that stall**: "In today's fast-paced world," "Let's dive in," "It's worth
  noting that," rhetorical questions, and a sentence that only announces the next
  sentence.
- **"It's not just X — it's Y"**, three-item flourishes, and the same em-dash rhythm in
  every paragraph. Vary sentence length instead.
- **A summary that repeats the intro.** End on the next action, a link, or nothing.
- **Promises the product doesn't keep.** Every guarantee in a document becomes a
  support ticket.

## Readers who aren't you

- Use **they/them** for a person whose pronouns you don't know; use roles ("the
  reviewer," "your admin") over invented names.
- Skip idioms, sports and war metaphors, and regional humor — they translate badly and
  age fast. Skip figures of speech that use disability as a flaw ("crazy," "blind to,"
  "tone-deaf"); say what you mean.
- **Absolute dates and units**: "2026-03-14, 09:00 UTC," not "next Tuesday." Give the
  unit and the timezone every time.
- **Describe the action, not the hardware**: "select," "open," "enter" work on mouse,
  touch, and keyboard.
- **Link text names the destination** — "Setup guide," not "click here." Images get
  alt text that states the point, not "screenshot."
- Assume the reader is competent and busy, not that they've read the previous page.

## Skeletons

**How-to / task guide** — Title is the task · What you need first (access, versions) ·
Numbered steps with end states · How to check it worked · What to do if it didn't ·
Related tasks.

**README / getting started** — What this is, in one sentence a stranger understands ·
Who it's for and what it replaces · Install and run, copy-pasteable · One real example
with its actual output · Where to go next · Where to get help.

**Release note / announcement** — What changed, in the reader's words · Why they should
care (the outcome, not the implementation) · What they need to do, and by when ·
What breaks and how to migrate · Where to report problems.

**Proposal / RFC** — The problem and who has it today · What we propose, in one
paragraph · Options considered and why this one · Cost, risk, and what we'd stop doing ·
What we need from you and by when.

**Runbook / troubleshooting** — Symptom as the reader sees it · How to confirm it's this
problem · Fix, numbered · How to verify recovery · When to escalate, and to whom.

Adapt freely; a skeleton is a starting order, not a schema.

## Before you ship

1. Read only the title and first three lines. Does a stranger know what this is and
   what to do? If not, the answer is buried.
2. Read only the headings. Do they tell the whole story in order?
3. Is every claim true and checkable? Anything you can't source becomes a `TODO`, not a
   confident sentence.
4. Can a reader tell, at each step, whether it worked?
5. Cut 10% without losing meaning. There's always 10%.
6. Read one paragraph aloud. If you run out of breath or stumble, split it.
7. Does anything imply the reader is slow — "simply," "just," "as everyone knows"?
8. Would the least experienced person in the audience get through it without asking a
   question you could have answered here?

## Fit it to your team

Your style guide, glossary, and product names override anything above — read them first
if the repo has them (`STYLE.md`, `CONTRIBUTING.md`, docs config), and match the
surrounding documents' formatting conventions. Keep one shared glossary so the same
concept keeps the same name across every document, and prefer editing an existing
document over adding a second one that says the same thing differently.
