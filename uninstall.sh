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

# Sweep the roots install.sh recorded for anything pointing into this repo. Walking
# only the skills that still EXIST here would strand links for skills since renamed or
# removed — and their displaced .maestro-bak files with them.
sweep_root() {
  local root="$1" entry
  [ -d "$root" ] || return 0
  for entry in "$root"/* "$root"/.[!.]*; do
    [ -e "$entry" ] || [ -L "$entry" ] || continue
    unlink_if_ours "$entry"
  done
}
if [ -f "$STATE/skill-roots" ]; then
  while IFS= read -r root; do [ -n "$root" ] && sweep_root "$root"; done <"$STATE/skill-roots"
fi
sweep_root "$HOME/.claude/commands"

for d in "$REPO"/skills/*/; do
  name="$(basename "$d")"
  # Clean the roots install.sh recorded, not the ones this shell happens to point at:
  # CODEX_HOME may have changed since, and a guess leaves symlinks and .maestro-bak
  # backups stranded. Fall back to the defaults when there is no record.
  if [ -f "$STATE/skill-roots" ]; then
    while IFS= read -r root; do
      [ -n "$root" ] && unlink_if_ours "$root/$name"
    done <"$STATE/skill-roots"
  else
    unlink_if_ours "$HOME/.claude/skills/$name"
    unlink_if_ours "$HOME/.codex/skills/$name"
    unlink_if_ours "$HOME/.agents/skills/$name"
    [ -n "${CODEX_HOME:-}" ] && unlink_if_ours "$CODEX_HOME/skills/$name"
  fi
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
