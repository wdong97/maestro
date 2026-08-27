---
description: Trade status with every live agent session in this repo and settle collisions
argument-hint: "[all | done <what landed> | <nothing = this repo>]"
---

Run a cross-session standup using the `standup` skill. Send the messages — this is not
a dry run.

If the args start with `done`/`landed`, skip discovery: send the **standup update**
notice (step 7 of the skill) to the peers your earlier split constrained, saying what's
finished, what's free for them now, what you're still holding, and any shared state you
changed. Then stop.

Otherwise:

1. `~/.claude/skills/standup/scripts/peers.sh --repo` for the collision surface in this
   repo (use no flag if the args say `all`/`everyone`), and `ListAgents` for the names.
2. If it reports no peers in this repo, say so and stop. Otherwise send ONE round of
   pings to EVERY session it listed, in a single batch of parallel `SendMessage` calls —
   each ping leads with YOUR six-line MINE block, then asks for theirs. No triage, no
   confirmation step.
3. While replies land, verify the contested working trees against git yourself.
4. Report the table, the ranked collisions, the agreed split, and who never answered.
5. Remember the debt: when your own slice lands or frees a file you claimed, send the
   update notice to the peers you constrained, without being asked again.

Do not ask a peer to revert, discard, force-push, or stop its work — bring that back here.

Scope: $ARGUMENTS
