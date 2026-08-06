#!/usr/bin/env bash
# maestro uninstall — remove symlinks that point into this repo, restore any
# .maestro-bak backups, and put git's core.hooksPath back the way install.sh
# found it. Leaves the repo itself and ~/.ensemble runtime untouched.
# Does NOT remove the @import lines (harmless; edit CLAUDE.md/AGENTS.md by hand).
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GITHOOKS="$HOME/.config/git/hooks"
STATE="$HOME/.config/maestro"
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
# mirror install.sh's bin/ loop — otherwise board/ensemble-tui/ensemble-web are left
# as symlinks that dangle the moment this repo moves or is deleted
for f in "$REPO"/bin/*; do
  [ -f "$f" ] || continue
  unlink_if_ours "$HOME/.local/bin/$(basename "$f")"
done
unlink_if_ours "$HOME/.claude/coding-guidelines.md"
unlink_if_ours "$HOME/.codex/coding-guidelines.md"
unlink_if_ours "$GITHOOKS/pre-push"

# Put core.hooksPath back only if install.sh is the one that changed it —
# otherwise every repo would keep pointing at a now-hookless directory.
cur="$(git config --global --get core.hooksPath || true)"
if [ "$cur" = "$GITHOOKS" ] && [ -f "$STATE/prev-hookspath" ]; then
  prev="$(cat "$STATE/prev-hookspath")"
  if [ -n "$prev" ]; then
    git config --global core.hooksPath "$prev"; note "restore core.hooksPath=$prev"
  else
    git config --global --unset core.hooksPath 2>/dev/null; note "unset core.hooksPath (it was unset before maestro)"
  fi
  rm -f "$STATE/prev-hookspath"; rmdir "$STATE" 2>/dev/null
elif [ "$cur" = "$GITHOOKS" ]; then
  note "left  core.hooksPath=$cur (this installer didn't set it — unset by hand if you want)"
fi

echo "maestro uninstalled. (@import lines left as-is; remove manually if desired.)"
