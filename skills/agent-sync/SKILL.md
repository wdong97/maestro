---
name: agent-sync
description: Keep Claude Code, Codex, and other coding agents synchronized through explicit handoff packets, session IDs, current repo state, verification status, and safe cross-agent consultation. Use when the user asks to sync agents, continue from another agent, link Claude and Codex sessions, hand work between agents, compare agent findings, or get any agent caught up without assuming hidden shared memory.
---

# Agent Sync

Use this skill to get one coding agent in sync with another. Do not assume agents share hidden memory. Sync through explicit state: session IDs, paths, handoff packets, git status, files touched, verification run, constraints, and open questions.

## Core Workflow

1. Identify the current owner: user, current agent, other agent, or both in read-only review.
2. Collect state. Prefer the bundled read-only script:

```bash
scripts/collect-agent-state.sh
```

Resolve the script path relative to this skill directory. If script execution is unavailable, gather the same facts manually.

3. Locate counterpart sessions only when useful. See `references/session-locations.md`.
4. Produce a handoff packet using `references/handoff-template.md`.
5. Decide the sync mode:
   - **Catch-up only**: summarize current state for this agent.
   - **Handoff**: prepare another agent to continue.
   - **Read-only consult**: ask another agent for a second opinion.
   - **Resume**: continue a named session ID.
   - **Merge findings**: compare outputs and verify claims.
6. Verify before acting. Treat another agent's output as a suggestion until confirmed against files, tests, docs, or fresh command output.

## Safety Rules

- Let only one agent edit a repo at a time.
- Default cross-agent calls to read-only.
- Do not stage, commit, push, delete, reset, or overwrite another agent's work unless the user explicitly asks.
- Do not paste secrets, tokens, private credentials, or unnecessary customer data into another agent prompt.
- If permissions or sandboxing block a needed cross-agent call, request approval instead of working around it.
- If two agents edited the same files, inspect the diff carefully and reconcile explicitly before continuing.

## Cross-Agent Prompts

### Ask Claude From Codex

```text
You are a peer agent helping Codex. Stay read-only.

Handoff packet:
{packet}

Return:
1. Confirmed understanding
2. Gaps or risks
3. Findings with file references
4. What Codex should verify before acting
5. Smallest safe next step
```

### Ask Codex From Claude

```text
You are a peer agent helping Claude. Stay read-only.

Handoff packet:
{packet}

Return:
1. Confirmed understanding
2. Gaps or risks
3. Findings with file references
4. What Claude should verify before acting
5. Smallest safe next step
```

## Resume Commands

Use exact session IDs when available.

Claude:

```bash
claude --resume "$CLAUDE_SESSION_ID" -p "$PROMPT" --output-format text
claude --continue -p "$PROMPT" --output-format text
```

Codex:

```bash
codex resume "$CODEX_SESSION_ID" "$PROMPT"
codex resume --last "$PROMPT"
codex exec -C "$REPO" --skip-git-repo-check --sandbox read-only -o "$OUT" "$PROMPT"
```

Use interactive resumes only when the environment supports an interactive TTY.

## Output

When the user asks to sync agents, return:

- Current state summary.
- Session IDs or session-log paths found.
- Active constraints and ownership.
- Files touched or risky overlap.
- Verification already run.
- Recommended next action.
- A copy-pasteable handoff packet if another agent should continue.
