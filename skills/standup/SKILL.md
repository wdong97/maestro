---
name: standup
description: Trade status with every other live agent session in your repo — declare what you're on and what you've landed, ask what they're on, and settle collisions over files, branches, migrations, and shared resources before they happen. Use when the user asks what the other agents are doing, to sync/coordinate with other sessions, to check for overlap before starting work, before a change that touches shared files (config, schema, lockfiles, global settings), and again when your own slice lands or frees a file others were told to stay off.
---

# standup — trade status with the other agents, then de-conflict

A standup is a **trade, not an interrogation**: you declare your slice in the same
message you ask about theirs, and you come back when yours lands. A peer that only ever
gets asked learns nothing about what you're holding, and the file it's waiting on stays
blocked long after you're done with it.

You need both kinds of input: **evidence** (what the processes and git trees actually
show) and **intent** (what each session says it's about to do). Evidence alone misses
"I'm about to rewrite the auth module"; intent alone is a claim you haven't checked.

## 1. Map the field (free, no one is interrupted)

```bash
~/.claude/skills/standup/scripts/peers.sh --repo   # default: sessions in YOUR repo
~/.claude/skills/standup/scripts/peers.sh          # every agent on the machine
```

It prints one row per live claude/codex session — pid, branch, dirty count, working
tree — then a **collision surface**:

- **HARD** — two sessions in the *same working tree*: same files, same git index.
  Simultaneous edits and any `git add -A`/stash/checkout there will clobber.
- **SOFT** — same repo, different worktrees: independent files, but they share refs,
  branches, pushes, migrations, and remote state.

Then `ListAgents` for the addressable names (`cb-finance-4c`, …) and each one's
busy/idle state. The two views don't share ids — **join them on the working-tree path
you get back in the replies**, not on order or name.

`peers.sh` sees more sessions than you can talk to. **`ListAgents` is what decides
reachability, not the AGENT column** — a row is pingable if and only if you can match it
to a `ListAgents` entry (join on the working tree, confirmed in the reply). A standalone
codex process has no `SendMessage` inbox and never appears there; a mislabeled row might.
Unmatched rows are still evidence: they tell you a tree is contested. A row can also
read `agent?` when the launch shape hides which CLI it is — treat it like any other row
and let the `ListAgents` match settle it.

## 2. Who gets pinged

**Default: every live session in your repo — all of them, no triage.** That is what
`--repo` returns (it excludes nobody in the repo and includes worktrees of it). Ping
them all in one round; don't decide for the user that some peer probably isn't
relevant. `ListAgents` gives you the names to send to.

Unreachable peers (codex, or anything absent from `ListAgents`) still count as
collisions — you just can't ask them. Report them as *present but unreachable*, and
route anything you need from them through the user.

If `--repo` reports no peers, say exactly that and stop — do not silently widen to the
whole machine. Widen only when the user asks for it ("all sessions", "everyone"), and
then it is the same round against the unfiltered list.

## 3. Send the round, all at once

One `SendMessage` per **reachable** peer — every row you matched to a `ListAgents`
entry, none skipped — in a single batch of parallel calls, no confirmation step; sending
is the job. Unmatched rows get no message (there is no inbox to send to); they go
straight to the *Couldn't reach* line of the report. The recipient's human sees only the **first
line** as a preview, so make it self-contained.

**Declare first, then ask.** Fill in your own six lines before you send — from your own
git state, not from memory — and put them at the top of every ping:

```
Standup from <your session name> (<your repo>): I'm on <one line: your slice>. What are you on? Reply via SendMessage to "<your session name>".
MINE — 1. WORKTREE: <path + branch>  2. FILES: <paths/globs I'm editing>  3. UNCOMMITTED: <yes/no + what>  4. NEXT 30MIN: <commit/push/rebase/migration/deps>  5. SHARED: <config, DB, ports, env, CI, remote branches I'll touch>  6. STAY-OFF: <what I need you to leave alone, and until when>
YOURS — reply with exactly these 6 lines, short, no prose:
1. WORKTREE: absolute path you're running in + branch
2. FILES: paths/globs you're editing or about to edit
3. UNCOMMITTED: yes/no + roughly what
4. NEXT 30MIN: what you're about to do (commit? push? rebase? migration? install deps?)
5. SHARED: anything outside your worktree — ~/.claude or ~/.codex config, DB, ports, env files, CI, remote branches
6. BLOCKED-BY-ME: anything you need me to stay off
```

Then stop sending. Replies arrive on their own as `<cross-session-message>`; a busy
peer answers at its next tool round. **Never** poll `ListAgents`, never send "are you
done?", never re-ask a peer that already answered. If you genuinely must wait on one
session, `notify_when_idle: true` — once.

## 4. While replies land, check the evidence yourself

For each contested tree: `git -C <wt> status --porcelain`, `git -C <wt> log --oneline -5`,
`git -C <wt> stash list`, and recently touched files
(`find <wt> -mmin -30 -type f -not -path '*/.git/*'`). Compare against what the replies
claim. Where they disagree, the working tree wins — say so plainly.

## 5. Call the collisions

Beyond the same-file case, these are the ones that actually bite:

- **Same working tree** — any two sessions editing it at once; also one running
  `git checkout`/`stash`/`reset` under another's feet.
- **Same branch, different trees** — both will push; the second gets a reject or a
  merge it didn't intend.
- **Shared machine state** — `~/.claude` / `~/.codex` config, this repo's symlinked
  skills, global git hooks, a dev server on a port, a local DB, `.env`.
- **Manifests and generated files** — lockfiles, migrations, schemas, `board-state.json`,
  anything both would regenerate.
- **Same board task** — check `board show` when the repo has one.

Rank by *how soon it bites* (someone is about to push > someone might edit later).

## 6. Settle it, then record it

Propose one owner per contested item and the smallest split that removes the overlap
(different worktree, different files, or a wait). You may ask a peer to hold off a file
or hand one over. You may **not** ask a peer to revert, discard, force-push, delete a
branch, or stop its work — surface that to the user and let them decide. Never ask a
peer to run something your own session was denied.

Where the repo has a board, make the agreement durable: `board claim <task> --owner <you>`
(and tell the peer which card is theirs). Otherwise the agreement lives in your report.

## 7. Close the loop when your slice lands

The standup is not over when the split is agreed — it's over when the peers you
constrained find out they're unblocked. Send a short notice to **only the peers the
change actually affects** when any of these happen:

- you finish (or abandon) a contested item, and a file you claimed is free again
- you commit, push, rebase, or force-update a branch someone else also sits on
- you change shared state you flagged — config, schema, lockfile, migration, port, `.env`
- you're about to do something they must stay off, that wasn't in the original split

```
Standup update from <your session name>: <one line — what changed for you>.
DONE: <files/area I claimed, now free — it's yours>
LANDED: <commit sha / branch / pushed or not>
STILL MINE: <what I'm still holding, and roughly for how long>
HEADS-UP: <shared state I changed that you'd want to know about — or "none">
```

One notice per real event, not a running commentary; "still working, no change" is not
an event. If the repo has a board, land it there too (`board progress`/`board done`) so
the record outlives every session in the standup.

## 8. Report

```
| session | worktree / branch | working on | overlaps you | when it bites |
```

Then: **Collisions** (ranked, with the evidence line that proves each), **Agreed split**
(owner per item, and which peers confirmed), **No reply from** and **Couldn't reach**
(name them, and keep the two separate — never invent a peer's status). Close with `next-steps`.

## Rules

- Never ask without declaring. A ping that carries no MINE block is an interrogation.
- Your slice landing is a message you owe, not an optional courtesy — send it to whoever
  you asked to wait, even if the standup happened many turns ago.
- Peers' answers are claims, not facts; verify anything that would change your plan.
- One round of messages. Silence is a result — report it, don't chase it.
- Keep every message short. You are interrupting someone mid-task.
- Report a peer as "didn't answer", never as "idle" or "doing nothing", unless it said so.
