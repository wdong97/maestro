#!/usr/bin/env bash
set -u

now="$(date -Is 2>/dev/null || date)"
cwd="$(pwd -P 2>/dev/null || pwd)"

echo "# Agent Sync State"
echo
echo "- collected_at: ${now}"
echo "- cwd: ${cwd}"

if [ -n "${CLAUDE_SESSION_ID:-}" ]; then
  echo "- current_agent_hint: claude"
  echo "- claude_session_id: ${CLAUDE_SESSION_ID}"
elif [ -n "${CODEX_SESSION_ID:-}" ]; then
  echo "- current_agent_hint: codex"
  echo "- codex_session_id: ${CODEX_SESSION_ID}"
else
  echo "- current_agent_hint: unknown"
fi

if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo
  echo "## Git"
  echo "- repo_root: $(git rev-parse --show-toplevel 2>/dev/null || true)"
  echo "- branch: $(git branch --show-current 2>/dev/null || true)"
  echo
  echo '```text'
  git status --short --branch 2>/dev/null || true
  echo '```'
fi

echo
echo "## Claude Sessions"
sanitized="$(printf '%s' "${cwd}" | sed 's#/#-#g')"
claude_dir="${HOME}/.claude/projects/${sanitized}"
echo "- project_dir: ${claude_dir}"
if [ -d "${claude_dir}" ]; then
  echo
  echo '```text'
  ls -1t "${claude_dir}"/*.jsonl 2>/dev/null | head -n 10 || true
  echo '```'
else
  echo "- project_dir_status: missing"
fi

echo
echo "## Codex Sessions"
codex_index="${HOME}/.codex/session_index.jsonl"
echo "- session_index: ${codex_index}"
if [ -f "${codex_index}" ]; then
  echo
  echo '```jsonl'
  tail -n 10 "${codex_index}" 2>/dev/null || true
  echo '```'
else
  echo "- session_index_status: missing"
fi
