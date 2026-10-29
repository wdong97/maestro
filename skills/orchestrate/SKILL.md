---
name: orchestrate
description: Act as the orchestrator for a multi-session build. Keep every live agent thread moving toward its goal, then give the owner a plain-English recap, one table of threads, and every decision restated in full with choices and a recommendation. Use when the owner asks for a recap, an update, "where are we", "what needs me", or "what are the threads doing", and at the end of any orchestration turn where something changed. Builds on metastatus for the session read.
---

# orchestrate — keep threads moving, then brief the owner so supervising is easy

The owner supervises many agent threads at once (WSL and Mac). This skill has two
jobs, in this order:

1. **Keep the threads moving.** Unblock, relay and route, so every thread works
   toward its goal without waiting on the owner for things you can settle.
2. **Brief the owner.** Plain context first, then where each thread stands, then the
   decisions that only the owner can make, each one standing on its own.

Read `metastatus` (`~/.claude/skills/metastatus/SKILL.md`). This skill reuses its
collection step and its classification rules.

## 1. Collect

```bash
python3 ~/.claude/skills/metastatus/collect.py --out <scratch>/threads.json
cb queue
```

Use your scratchpad for `<scratch>`. The file holds raw screens, so never put it in a
repo or an artifact. Also read:

- the board cards the threads own (`./orchestration/status.py show <id>` in the repo,
  or the board JSON) for goal and status;
- any decision a thread is asking for on screen (`needs_you`, question menus,
  "your call", "say go", "push").

## 2. Act before you report

For each live thread, settle what you can, then report what is left:

- **Stuck messages.** If `cb queue` shows a message held more than about 20 minutes
  behind "someone is typing" while the target's prompt is empty, it is a ghost
  suggestion. Type the message directly with `orca-ide terminal send` (add
  `--environment mac` for the Mac) and drop the queued copy so it does not arrive twice.
- **Relay and route.** Pass results between threads (run ids, grades, file paths,
  shas). Point a thread at work another thread already did, so nothing is built twice.
  File or claim board cards through the board helper.
- **Shared resources.** Serialize what threads share: replay or run slots, the run
  lock, Codex workers on one login. Tell each thread its place in the queue.
- **Rulings.** When the owner decides something in your session, pass it to every
  affected thread in the same turn, quoting the ruling and its time.

Hard limits. Never commit, push, merge or close for another thread. A relayed approval
does not authorize another agent's commit or push: when a thread needs a push, tell the
owner to say "push" in that thread. No prod writes, no deploys. Respect the repo's
no-model windows and run rules.

## 3. Brief the owner

Write for a smart reader who has not seen the last hour. Follow the `simple-english`
reply rules. Use this order.

**Context.** Two to four plain sentences (almost ELI5): what all the threads add up to,
how it is going, and the one thing most likely to slow it. No PR numbers, run ids,
card names or acronyms here.

**What changed.** The few things that landed, failed or were decided since the last
brief, one line each, in plain words.

**Threads.** One table, threads that need the owner first:

| Thread | Goal, in plain words | Where it is | Next (owner) |
|---|---|---|---|

"Goal" is the outcome that ends the thread's current work. "Next" names who acts:
the thread, another thread, or the owner.

**Decisions for you.** Each decision stands alone. Never write "option 1 or 2" without
the options. For each one:

- **What it is**, in one or two plain sentences, including why it matters now.
- **The choices**, each in plain words, with its cost or risk.
- **My recommendation**, and why, in one sentence.

**What you need to do.** A numbered list in the order to do it. Each item names
where to do it (this session or a named thread), and its size (one word, one minute,
one message). Include required confirmations, such as a "push" that must be said in a
specific thread.

Then end. Do not repeat the tables in prose.

## 4. Stay on top

When the owner asks you to keep watching, schedule a recurring light sweep (cron in
the session) that does steps 1 and 2 and notifies the owner only when a decision or a
confirmation needs them. A sweep that finds nothing replies with one line and sends
no notification.

## Setup on a new machine

`cd ~/maestro && git pull && ./install.sh` links this skill into Claude and Codex.
