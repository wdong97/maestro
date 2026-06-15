#!/usr/bin/env bash
# maestro uninstall — remove symlinks that point into this repo and restore any
# .maestro-bak backups. Leaves the repo itself and ~/.ensemble runtime untouched.
# Does NOT remove the @import lines (harmless; edit CLAUDE.md/AGENTS.md by hand).
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
note() { printf '  %s\n' "$*"; }

# unlink_if_ours <linkpath> — if it's a symlink into REPO, remove it and restore backup.
unlink_if_ours() {
  local dest="$1"
  if [ -L "$dest" ] && [[ "$(readlink -f "$dest")" == "$REPO"/* ]]; then
    rm -f "$dest"; note "rm    $dest"
    if [ -e "$dest.maestro-bak" ]; then mv "$dest.maestro-bak" "$dest"; note "restore $dest"; fi
  fi
}

for d in "$REPO"/skills/*/; do
  name="$(basename "$d")"
  unlink_if_ours "$HOME/.claude/skills/$name"
  unlink_if_ours "$HOME/.codex/skills/$name"
done
for f in "$REPO"/commands/*.md; do unlink_if_ours "$HOME/.claude/commands/$(basename "$f")"; done
unlink_if_ours "$HOME/.local/bin/ensemble"
unlink_if_ours "$HOME/.claude/coding-guidelines.md"
unlink_if_ours "$HOME/.codex/coding-guidelines.md"
unlink_if_ours "$HOME/.config/git/hooks/pre-push"

echo "maestro uninstalled. (core.hooksPath and @import lines left as-is; remove manually if desired.)"
