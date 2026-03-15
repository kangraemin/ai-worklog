#!/bin/bash
# worklog-for-claude uninstaller
# Removes hooks, scripts, and config installed by install.sh
# Preserves: .worklogs/ data and .env (Notion credentials)

set -euo pipefail

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${BLUE}i${NC}  $*"; }
ok()    { echo -e "${GREEN}✓${NC}  $*"; }
warn()  { echo -e "${YELLOW}!${NC}  $*"; }
err()   { echo -e "${RED}x${NC}  $*" >&2; }
header(){ echo -e "\n${BOLD}${CYAN}── $* ──${NC}\n"; }

# ── Help ─────────────────────────────────────────────────────────────────────
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: ./uninstall.sh [OPTIONS]

Removes worklog-for-claude hooks, scripts, commands, and config.

Options:
  --help, -h     Show this help message
  --dry-run      Show what would be removed without making changes
  --global       Uninstall from ~/.claude/ (default: auto-detect)
  --local        Uninstall from .claude/ in current directory

Preserved (never deleted):
  .worklogs/     Your worklog data
  .env           Notion credentials
EOF
  exit 0
fi

# ── Parse arguments ──────────────────────────────────────────────────────────
DRY_RUN=false
SCOPE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)  DRY_RUN=true ;;
    --global)   SCOPE="global" ;;
    --local)    SCOPE="local" ;;
    *)          err "Unknown option: $1"; exit 1 ;;
  esac
  shift
done

# ── Detect install scope ────────────────────────────────────────────────────
if [ -z "$SCOPE" ]; then
  if [ -f ".claude/hooks/post-commit.sh" ] && grep -q "worklog" ".claude/hooks/post-commit.sh" 2>/dev/null; then
    SCOPE="local"
  elif [ -f "$HOME/.claude/hooks/post-commit.sh" ] && grep -q "worklog" "$HOME/.claude/hooks/post-commit.sh" 2>/dev/null; then
    SCOPE="global"
  else
    echo "Where is worklog-for-claude installed?"
    echo "  1) Global (~/.claude/)"
    echo "  2) Local (.claude/)"
    echo ""
    printf "Select [1]: "
    read -r SCOPE_CHOICE
    SCOPE_CHOICE="${SCOPE_CHOICE:-1}"
    [ "$SCOPE_CHOICE" = "2" ] && SCOPE="local" || SCOPE="global"
  fi
fi

if [ "$SCOPE" = "local" ]; then
  TARGET_DIR="$(pwd)/.claude"
else
  TARGET_DIR="$HOME/.claude"
fi

header "worklog-for-claude uninstaller"
info "Target: $TARGET_DIR"
info "Scope:  $SCOPE"
if [ "$DRY_RUN" = true ]; then
  warn "DRY RUN — no changes will be made"
fi
echo ""

# ── Confirmation ─────────────────────────────────────────────────────────────
if [ "$DRY_RUN" = false ]; then
  printf "Proceed with uninstall? [y/N]: "
  read -r CONFIRM
  if [[ ! "$CONFIRM" =~ ^[yY] ]]; then
    info "Cancelled."
    exit 0
  fi
fi

# ── Helper: safe remove ─────────────────────────────────────────────────────
remove_file() {
  local f="$1"
  if [ -f "$f" ]; then
    if [ "$DRY_RUN" = true ]; then
      info "[dry-run] Would remove: $f"
    else
      rm -f "$f"
      ok "Removed: $(basename "$f")"
    fi
  fi
}

remove_dir() {
  local d="$1"
  if [ -d "$d" ]; then
    # Only remove if directory is empty or contains only worklog files
    if [ "$DRY_RUN" = true ]; then
      info "[dry-run] Would remove directory: $d"
    else
      rm -rf "$d"
      ok "Removed directory: $(basename "$d")"
    fi
  fi
}

# ── 1. Remove installed files ───────────────────────────────────────────────
header "Removing installed files"

# Scripts
SCRIPTS=(
  "scripts/notion-worklog.sh"
  "scripts/notion-migrate-worklogs.sh"
  "scripts/duration.py"
  "scripts/token-cost.py"
  "scripts/update-check.sh"
  "scripts/worklog-write.sh"
)

for s in "${SCRIPTS[@]}"; do
  remove_file "$TARGET_DIR/$s"
done

# Remove scripts/ dir if empty
if [ -d "$TARGET_DIR/scripts" ]; then
  if [ "$DRY_RUN" = false ] && [ -z "$(ls -A "$TARGET_DIR/scripts" 2>/dev/null)" ]; then
    rmdir "$TARGET_DIR/scripts" 2>/dev/null && ok "Removed empty directory: scripts/"
  fi
fi

# Hooks
HOOKS=(
  "hooks/worklog.sh"
  "hooks/session-end.sh"
  "hooks/post-commit.sh"
  "hooks/stop.sh"
)

for h in "${HOOKS[@]}"; do
  remove_file "$TARGET_DIR/$h"
done

if [ -d "$TARGET_DIR/hooks" ]; then
  if [ "$DRY_RUN" = false ] && [ -z "$(ls -A "$TARGET_DIR/hooks" 2>/dev/null)" ]; then
    rmdir "$TARGET_DIR/hooks" 2>/dev/null && ok "Removed empty directory: hooks/"
  fi
fi

# Commands
COMMANDS=(
  "commands/worklog.md"
  "commands/migrate-worklogs.md"
  "commands/update-worklog.md"
  "commands/finish.md"
)

for c in "${COMMANDS[@]}"; do
  remove_file "$TARGET_DIR/$c"
done

if [ -d "$TARGET_DIR/commands" ]; then
  if [ "$DRY_RUN" = false ] && [ -z "$(ls -A "$TARGET_DIR/commands" 2>/dev/null)" ]; then
    rmdir "$TARGET_DIR/commands" 2>/dev/null && ok "Removed empty directory: commands/"
  fi
fi

# Rules
RULES=(
  "rules/worklog-rules.md"
  "rules/auto-commit-rules.md"
)

for r in "${RULES[@]}"; do
  remove_file "$TARGET_DIR/$r"
done

if [ -d "$TARGET_DIR/rules" ]; then
  if [ "$DRY_RUN" = false ] && [ -z "$(ls -A "$TARGET_DIR/rules" 2>/dev/null)" ]; then
    rmdir "$TARGET_DIR/rules" 2>/dev/null && ok "Removed empty directory: rules/"
  fi
fi

# Git hooks
remove_file "$TARGET_DIR/git-hooks/post-commit"

if [ -d "$TARGET_DIR/git-hooks" ]; then
  if [ "$DRY_RUN" = false ] && [ -z "$(ls -A "$TARGET_DIR/git-hooks" 2>/dev/null)" ]; then
    rmdir "$TARGET_DIR/git-hooks" 2>/dev/null && ok "Removed empty directory: git-hooks/"
  fi
fi

# Version file
remove_file "$TARGET_DIR/.version"

# Backup files (.bak)
for bak in "$TARGET_DIR"/scripts/*.bak "$TARGET_DIR"/hooks/*.bak "$TARGET_DIR"/commands/*.bak "$TARGET_DIR"/rules/*.bak; do
  [ -f "$bak" ] && remove_file "$bak"
done

# ── 2. Clean settings.json ──────────────────────────────────────────────────
header "Cleaning settings.json"

SETTINGS_FILE="$TARGET_DIR/settings.json"

if [ -f "$SETTINGS_FILE" ]; then
  if command -v python3 &>/dev/null; then
    PYTHON=python3
  elif command -v python &>/dev/null; then
    PYTHON=python
  else
    warn "python3 not found — skipping settings.json cleanup"
    PYTHON=""
  fi

  if [ -n "${PYTHON:-}" ]; then
    if [ "$DRY_RUN" = true ]; then
      info "[dry-run] Would clean worklog hooks and env from: $SETTINGS_FILE"
    else
      $PYTHON - "$SETTINGS_FILE" "$TARGET_DIR" <<'PYEOF'
import json, sys, os

settings_file = sys.argv[1]
target_dir = sys.argv[2]

with open(settings_file, encoding='utf-8') as f:
    cfg = json.load(f)

# Remove WORKLOG_* and AI_WORKLOG_DIR env variables
env = cfg.get('env', {})
keys_to_remove = [k for k in env if k.startswith('WORKLOG_') or k == 'AI_WORKLOG_DIR']
for k in keys_to_remove:
    del env[k]
    print(f'  Removed env: {k}')

# Remove worklog-related hooks
WORKLOG_MARKERS = [
    'worklog.sh', 'session-end.sh', 'post-commit.sh',
    'stop.sh', 'update-check.sh', '/finish'
]

hooks = cfg.get('hooks', {})
for event in list(hooks.keys()):
    original = hooks[event]
    filtered = []
    for group in original:
        group_hooks = group.get('hooks', [])
        clean_hooks = [
            h for h in group_hooks
            if not any(
                m in h.get('command', '') or m in h.get('prompt', '')
                for m in WORKLOG_MARKERS
            )
        ]
        if clean_hooks:
            group['hooks'] = clean_hooks
            filtered.append(group)
    if filtered:
        hooks[event] = filtered
    else:
        del hooks[event]
        print(f'  Removed hook event: {event}')

# Remove empty sections
if not env:
    cfg.pop('env', None)
if not hooks:
    cfg.pop('hooks', None)

with open(settings_file, 'w', encoding='utf-8') as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
    f.write('\n')

print(f'  Updated: {settings_file}')
PYEOF
      ok "settings.json cleaned"
    fi
  fi
else
  info "No settings.json found — skipping"
fi

# ── 3. Reset git config (global scope) ──────────────────────────────────────
header "Git config cleanup"

if [ "$SCOPE" = "global" ]; then
  CURRENT_HOOKS_PATH=$(git config --global core.hooksPath 2>/dev/null || true)
  GIT_HOOKS_DIR="$TARGET_DIR/git-hooks"

  if [ "$CURRENT_HOOKS_PATH" = "$GIT_HOOKS_DIR" ]; then
    if [ "$DRY_RUN" = true ]; then
      info "[dry-run] Would unset git config --global core.hooksPath"
    else
      git config --global --unset core.hooksPath
      ok "Unset global core.hooksPath"
    fi
  elif [ -n "$CURRENT_HOOKS_PATH" ]; then
    info "core.hooksPath ($CURRENT_HOOKS_PATH) is not worklog — skipping"
  else
    info "No global core.hooksPath set — skipping"
  fi
else
  # Local: restore .git/hooks/post-commit.local if it exists
  REPO_GIT_DIR=$(git rev-parse --git-dir 2>/dev/null || true)
  if [ -n "$REPO_GIT_DIR" ]; then
    LOCAL_HOOK="$REPO_GIT_DIR/hooks/post-commit"
    LOCAL_BACKUP="${LOCAL_HOOK}.local"
    if [ -f "$LOCAL_HOOK" ] && grep -q "worklog" "$LOCAL_HOOK" 2>/dev/null; then
      if [ "$DRY_RUN" = true ]; then
        info "[dry-run] Would remove: $LOCAL_HOOK"
        [ -f "$LOCAL_BACKUP" ] && info "[dry-run] Would restore: $LOCAL_BACKUP → $LOCAL_HOOK"
      else
        rm -f "$LOCAL_HOOK"
        if [ -f "$LOCAL_BACKUP" ]; then
          mv "$LOCAL_BACKUP" "$LOCAL_HOOK"
          ok "Restored original post-commit hook from .local backup"
        else
          ok "Removed worklog post-commit hook"
        fi
      fi
    fi
  fi
fi

# ── 4. Summary ──────────────────────────────────────────────────────────────
header "Uninstall complete"

echo -e "  ${BOLD}Preserved${NC} (not deleted):"
echo "  ├─ .worklogs/   — your worklog data"
echo "  ├─ .env         — Notion credentials"
echo "  └─ NOTION_DB_ID — remove manually from settings.json if needed"
echo ""
if [ "$DRY_RUN" = true ]; then
  warn "This was a dry run. Re-run without --dry-run to apply changes."
else
  ok "worklog-for-claude has been uninstalled."
fi
