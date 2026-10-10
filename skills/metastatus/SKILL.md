---
name: metastatus
description: One table per machine (WSL and Mac) of every live agent session — what it is working on, how far the work got, the goal, and whether to keep it, close it out, or answer it. Reads each session's last screen through `cb` and Orca; never messages anyone. Use when the user asks what the threads/sessions/agents are doing, which can be closed, or for status across machines.
---

# metastatus — every live session, one table per machine

Read-only. You read screens; you never `cb send`, never type into a terminal, never
close anything. Closing is the user's call.

## 1. Collect (one command, ~10 s)

```bash
python3 ~/.claude/skills/metastatus/collect.py --out <scratch>/threads.json
```

Use your scratchpad (or a temp dir) for `<scratch>`; the file holds raw screens and can
show private data, so never put it in a repo or an artifact. The script needs `cb` on
PATH (agent-memory repo) and works the same from either machine. Read the whole file.

It gives `sessions` (registered, not gone, each with `scope`, `state`, `screen`,
`self_recap`, `needs_you`, `read_ok`), `gone` (labels only), and `unregistered`
(terminals with no `cb` label: title + screen). Your own terminal has `is_me: true` and
no screen; fill its row from your own context.

## 2. Classify each live session from its screen

For each one, decide, in your own words:

- **Working on** — the concrete task on screen now (PR number, run id, card), not the scope line.
- **Status** — one of: `running` (busy, doing work), `waiting on <who/what>`,
  `done` (its last message reports the work landed and nothing is pending),
  `blocked: <reason>`, `needs you` (a permission prompt or a question to the user on screen).
- **Goal** — the specific outcome that ends this session's current work, with its finish
  line: what lands or gets decided, and by when or after what. Name the PR, run, card or
  decision. Write "#792 merged ON before Sun 18:00 so Monday's run uses fusion", not
  "ADR 0085 fusion stack"; "owner decides on Tue optimizer flip from Mon run", not
  "conviction optimizer". The `scope` line is only a starting point; the screen (latest
  plan, next steps, recap) decides. If no finish line is visible, say "no finish line on screen".
- **Disposition** — `keep` (has live or scheduled work), `close out` (its work merged or
  was handed off and nothing is pending — say what proves it), `answer` (needs the user
  now), `check` (screen unreadable or ambiguous; say why).

Evidence rules: the screen is the evidence. `state: idle` alone does not mean done; an
idle session can be waiting on a merge or a slot. If `read_ok` is false, write
"could not read" — never guess. Never quote figures, holdings, tokens, or account data
from a screen; summarize.

## 3. Report

Start with **Overall**: three short sentences, before any table, that a smart
friend outside the project understands on one read (almost ELI5):

1. **What we are doing** — the one big thing all the sessions add up to, in everyday
   words ("getting this week's improvements into Monday morning's run").
2. **How it is going** — a plain count or picture of progress ("most of it is in; three
   pieces are left").
3. **What we are trying to get through** — the next deadline and the one thing most
   likely to miss it ("everything must be in by Sunday 6 pm; the riskiest piece is X").

Rules: no PR numbers, version numbers, run ids, card names or acronyms here (they belong
in the tables); no jargon a newcomer would not know; under 20 words per sentence. Derive
it from the goals and statuses you classified; do not invent a goal no session shows. If
the sessions do not share one push, give one plain sentence per project instead.

Then one table per machine, live sessions only, `needs you` and `answer` rows first:

| Session | Working on | Status | Goal | Disposition |
|---|---|---|---|---|

Then, in this order:

1. **Close now** — the `close out` sessions, each with its one-line proof.
2. **Needs you** — each with what it is asking.
3. **Gone** — one line per machine: count + labels. These terminals are already dead;
   nothing to close.
4. **Unregistered** — a short table (machine, title, state, one-line guess at the work)
   for agent terminals; plain shells in one line. Note that `cb send` cannot reach them
   until they run `cb register <machine>/<name>`.

No recommendations beyond the disposition column, and no next-work plan. Stop after the report.

## Setup on a new machine

`cd ~/maestro && git pull && ./install.sh` links this skill into Claude and Codex. `cb`
comes from the agent-memory repo (`~/.local/bin/cb`).
