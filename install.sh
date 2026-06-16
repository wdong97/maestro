#!/usr/bin/env bash
# maestro install — wire this repo into the local Claude Code + Codex setup.
# The repo is the single source of truth; home-dir locations become symlinks into
# it, so editing a file here is live and `git pull` updates the whole system.
# Idempotent. Existing non-maestro files are backed up to <path>.maestro-bak.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"
CODEX="$HOME/.codex"
BIN="$HOME/.local/bin"
GITHOOKS="$HOME/.config/git/hooks"

note() { printf '  %s\n' "$*"; }

# link <target> <linkpath> — point linkpath at target, backing up anything real.
link() {
  local target="$1" dest="$2"
  if [ -L "$dest" ] && [ "$(readlink -f "$dest")" = "$(readlink -f "$target")" ]; then
    note "ok    $dest"; return
  fi
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if [ ! -e "$dest.maestro-bak" ]; then mv "$dest" "$dest.maestro-bak"; note "bak   $dest -> $dest.maestro-bak"
    else rm -rf "$dest"; fi
  fi
  mkdir -p "$(dirname "$dest")"
  ln -sfn "$target" "$dest"
  note "link  $dest -> $target"
}

# ensure_import <file> <line> — append an @import line if not already present.
ensure_import() {
  local file="$1" line="$2"
  mkdir -p "$(dirname "$file")"; touch "$file"
  grep -qxF "$line" "$file" || printf '%s\n' "$line" >>"$file"
  note "import $file  <=  $line"
}

echo "maestro install from: $REPO"

echo "[skills] -> ~/.claude/skills and ~/.codex/skills"
for d in "$REPO"/skills/*/; do
  name="$(basename "$d")"
  link "$d" "$CLAUDE/skills/$name"
  link "$d" "$CODEX/skills/$name"
done

echo "[commands] -> ~/.claude/commands (Claude slash commands)"
for f in "$REPO"/commands/*.md; do link "$f" "$CLAUDE/commands/$(basename "$f")"; done

echo "[cli] -> ~/.local/bin/ensemble"
chmod +x "$REPO/skills/ensemble/scripts/ensemble.sh"
link "$REPO/skills/ensemble/scripts/ensemble.sh" "$BIN/ensemble"
case ":$PATH:" in *":$BIN:"*) ;; *) note "WARN  $BIN is not on PATH — add it to your shell rc";; esac

if [ -d "$REPO/bin" ]; then
  echo "[bin] -> ~/.local/bin (tui, future tools)"
  for f in "$REPO"/bin/*; do [ -f "$f" ] || continue; chmod +x "$f"; link "$f" "$BIN/$(basename "$f")"; done
fi

echo "[guidelines] -> both homes + @import"
link "$REPO/guidelines/coding-guidelines.md" "$CLAUDE/coding-guidelines.md"
link "$REPO/guidelines/coding-guidelines.md" "$CODEX/coding-guidelines.md"
ensure_import "$CLAUDE/CLAUDE.md" "@coding-guidelines.md"
ensure_import "$CODEX/AGENTS.md"  "@$HOME/.codex/coding-guidelines.md"

echo "[hook] global pre-push peer review"
chmod +x "$REPO/hooks/pre-push"
link "$REPO/hooks/pre-push" "$GITHOOKS/pre-push"
cur="$(git config --global --get core.hooksPath || true)"
if [ "$cur" != "$GITHOOKS" ]; then git config --global core.hooksPath "$GITHOOKS"; note "set   core.hooksPath=$GITHOOKS"
else note "ok    core.hooksPath=$GITHOOKS"; fi

echo
echo "maestro installed. Verify with:  ensemble doctor"
echo "(slash commands / skills load in NEW agent sessions.)"
