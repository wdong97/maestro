# Session Locations

Use these locations to find explicit continuation points.

## Claude Code

Personal skills:

```text
~/.claude/skills/<skill-name>/SKILL.md
```

Project session logs:

```text
~/.claude/projects/<sanitized-project-path>/<session-id>.jsonl
```

The sanitized path usually replaces `/` with `-`, so `/home/wdong/devel/admin` becomes:

```text
~/.claude/projects/-home-wdong-devel-admin/
```

Useful CLI shapes:

```bash
claude --continue -p "$PROMPT" --output-format text
claude --resume "$CLAUDE_SESSION_ID" -p "$PROMPT" --output-format text
```

## Codex

Personal skills:

```text
~/.codex/skills/<skill-name>/SKILL.md
```

Session index and logs:

```text
~/.codex/session_index.jsonl
~/.codex/sessions/YYYY/MM/DD/rollout-...jsonl
```

Useful CLI shapes:

```bash
codex resume "$CODEX_SESSION_ID" "$PROMPT"
codex resume --last "$PROMPT"
codex exec -C "$REPO" --skip-git-repo-check --sandbox read-only -o "$OUT" "$PROMPT"
```

## Shared Rule

Session logs are evidence, not authority. After reading or resuming a session, verify claims against the current files and command output.
