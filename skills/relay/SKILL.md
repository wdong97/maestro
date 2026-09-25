---
name: relay
description: Drive a long-lived dev agent (Claude or Codex) hop by hop instead of the user copy-pasting prompts in and reports out — draft each prompt, get the user's "go", send it to the same dev session, check its RELAY-REPORT against git, then draft the next. Use when the user says relay, "give me the next prompt for the dev agent", hand this to the dev agent, or wants an orchestrator/dev split on a multi-phase build.
---

# relay — the orchestrator carries the messages, the user keeps the "go"

You are the orchestrator. The dev agent is one long-lived session that keeps its
context across hops. You write its prompts and read its reports; the user approves
every hop and no longer copies text between windows.

## Set up once

```bash
ensemble relay new NAME --to codex|claude --dir <repo or worktree> [--mx M | --mc M] [--eff E]
```

One relay per working tree, and nobody else edits that tree while it runs.

## Each hop

1. **Draft** the next prompt: goal, what's already done (with commit SHAs), scope
   and no-scope, numbered requirements, how to verify. Keep the user's standing
   additions — branch steps ("cut a new branch from main"), "use subagents if needed",
   "nothing hardcoded".
2. **Show it and stop.** The user says "go", edits it, or stops. No hop is sent
   without that "go" — this is the start-task gate, once per hop.
3. **Send and wait:**
   ```bash
   ensemble relay send NAME prompt.md      # or: ... | ensemble relay send NAME -
   ensemble relay wait NAME                # blocks (default 2h); prints the RELAY-REPORT
   ```
   Hops run a median of ~20 minutes: run `wait` in the background and let its exit
   wake you, rather than polling. The user can watch live: `tmux attach -t ensemble`.
4. **Check the report against git, never on its word.** The commit exists
   (`git -C <dir> cat-file -e SHA`), is on the branch it names, and — if it says
   pushed — is on the remote. Re-run a test it claims when that's cheap. A missing
   RELAY-REPORT block means the hop did not finish cleanly: read `hop-N.out`.
5. **Tell the user** in plain words what the hop did, what checked out, what didn't,
   and show the next draft. Back to step 2.

`ensemble relay status NAME` lists every hop; prompts and answers stay in
`~/.ensemble/relay/NAME/hop-N.{prompt,out}`.

## Rules

- **Push and eval are their own hops.** The report block tells the dev agent not to
  push unless the prompt says it's a push hop. Anything that pushes, runs a paid
  eval, or spends money is a separate hop the user approves by name.
- **Stop on `blocked` or `needs-input`.** Bring it to the user with the dev agent's
  words; don't improvise a workaround hop.
- **Codex can't commit headless in its default sandbox.** `workspace-write` protects
  `.git` and there's no approval prompt to lift it, so a Codex dev hop that tries to
  commit reports `blocked`. Plan for that until the user picks how commits happen.
- **One deliverable per relay.** If the goal changes, that's a new task — intake
  starts over.
