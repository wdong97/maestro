---
name: start-task
description: Intake for every new task — frame the ask, explore where it lands, ask every real fork in one batch, write a one-minute plan, then stop and wait for the user's "go" before any repo write. Use at the start of every new task however small, when a follow-up changes the goal or deliverable, and whenever the user says start task, plan this first, or don't touch anything until I approve.
---

# start-task — nothing gets written until you say "go"

Before a builder touches your house, they check what you want, look at the house, ask
about anything they'd otherwise have to guess, and show you a short plan. They don't
pick up a hammer until you say "go." Anything extra they spot along the way goes on a
list for later, not into the current job.

## When it applies

- Every new task begins with start-task, however small it is.
- A follow-up inside the same task continues that task. A new goal or deliverable
  starts intake again.
- Questions, research and investigation skip the ritual. The gate applies as soon as
  the work turns into a repo write.
- Calling a skill directly (`/tdd`, `/delegate`, …) skips the intake steps but not the
  approval gate.

## The five steps

| # | Step | What happens | Done when |
|---|------|--------------|-----------|
| 1 | **Frame** | Restate the ask in 1–2 sentences: what gets delivered and where it'll be checked in the running system. Name what's out of scope. | The user would say "yes, that's what I asked for." |
| 2 | **Explore** | Find where the work lands and what already exists. Check for overlap with other sessions (`/standup`) and board cards (`/board`), and read the repo's CLAUDE.md/AGENTS.md and memory for rules and past lessons. Searches or reads of 3+ files go to subagents. | Every plan step names its exact files and constraints. Anything still unknown is listed openly. |
| 3 | **Ask** | Put every real fork to the user in one batch of questions, recommended option first: deleting a capability, trust rules, backend contracts, credentials, spending, anything hard to undo. Forks block until answered. Structure, state, naming and layout calls are the agent's to make, logged as proposed. | Every fork is answered, or the agent writes "No questions — no genuine forks." |
| 4 | **Plan** | A short plan readable in under a minute that covers every write the task will make: numbered steps (each with how it gets checked), expected complexities and how to handle them, and a one-line routing. Copy it into the agent's in-session task list (its todo tool, not a repo file) so it survives a context reset — that copy isn't a repo write and needs no approval. | — |
| 5 | **Gate** | Stop and wait for the user's "go." Then run the plan as approved. A write the plan didn't include isn't approved. | — |

## Rules around the steps

- **Routing announcement.** Before the first real tool call, one line naming the skill
  and delegation route, e.g. "Routing: frontend-design skill, then delegating 4 files →
  2 codex agents via /delegate."
- **Skill check, then delegation check.** Use a matching skill first. Then delegate via
  `/delegate` if the work touches 3+ files, needs a search, runs tests or builds, or has
  multiple steps. When unsure, delegate.
- **No scope creep mid-task.** New findings or "also fix this" items get parked and
  brought to the user as one batch after the approved plan is finished. If the
  deliverable itself changes, intake starts over at step 1.
- **Plain-language questions.** Options are written so a non-expert could choose, with
  jargon only after the idea is agreed.
