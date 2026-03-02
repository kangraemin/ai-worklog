#!/bin/bash
# worklog-for-claude 자동 업데이트 체커
# Usage: update-check.sh [--force] [--check-only]
#   --force      : 24h throttle 무시하고 즉시 체크
#   --check-only : 버전 확인만 (업데이트 안 함)

set -euo pipefail

REPO="kangraemin/worklog-for-claude"
RAW_BASE="https://raw.githubusercontent.com/$REPO/main"
API_URL="https://api.github.com/repos/$REPO/commits/main"

AI_WORKLOG_DIR="${AI_WORKLOG_DIR:-$HOME/.claude}"
VERSION_FILE="$AI_WORKLOG_DIR/.version"
CHECKED_FILE="$AI_WORKLOG_DIR/.version-checked"

FORCE=false
CHECK_ONLY=false
for arg in "$@"; do
  case $arg in
    --force)      FORCE=true ;;
    --check-only) CHECK_ONLY=true ;;
  esac
done

# ── 24시간 throttle ───────────────────────────────────────────────────────────
if [ "$FORCE" = false ] && [ -f "$CHECKED_FILE" ]; then
  LAST=$(cat "$CHECKED_FILE" 2>/dev/null || echo 0)
  NOW=$(date +%s)
  DIFF=$(( NOW - LAST ))
  if [ "$DIFF" -lt 86400 ]; then
    exit 0
  fi
fi

# ── 최신 SHA 조회 ────────────────────────────────────────────────────────────
LATEST_SHA=$(curl -sf --max-time 5 "$API_URL" 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d['sha'][:7])
except:
    sys.exit(1)
" 2>/dev/null) || {
  # 네트워크 실패 시 조용히 종료
  exit 0
}

# 체크 타임스탬프 갱신
date +%s > "$CHECKED_FILE"

# ── 설치된 버전 확인 ─────────────────────────────────────────────────────────
INSTALLED_SHA=$(cat "$VERSION_FILE" 2>/dev/null || echo "unknown")

if [ "$CHECK_ONLY" = true ]; then
  echo "installed: $INSTALLED_SHA"
  echo "latest:    $LATEST_SHA"
  if [ "$LATEST_SHA" = "$INSTALLED_SHA" ]; then
    echo "status: up-to-date"
  else
    echo "status: update-available"
  fi
  exit 0
fi

# ── 업데이트 필요 없으면 종료 ────────────────────────────────────────────────
if [ "$LATEST_SHA" = "$INSTALLED_SHA" ]; then
  exit 0
fi

# ── 자기 자신 먼저 업데이트 (bootstrap) ────────────────────────────────────────
SELF="scripts/update-check.sh"
SELF_DST="$AI_WORKLOG_DIR/$SELF"
if [ -f "$SELF_DST" ]; then
  SELF_TMP=$(mktemp)
  if curl -sf --max-time 10 "$RAW_BASE/$SELF" -o "$SELF_TMP" 2>/dev/null; then
    if ! cmp -s "$SELF_DST" "$SELF_TMP"; then
      mv "$SELF_TMP" "$SELF_DST"
      chmod +x "$SELF_DST" 2>/dev/null || true
      exec bash "$SELF_DST" --force "$@"
    fi
    rm -f "$SELF_TMP"
  else
    rm -f "$SELF_TMP"
  fi
fi

# ── 파일 다운로드 + 교체 ─────────────────────────────────────────────────────
FILES=(
  "scripts/notion-worklog.sh"
  "scripts/notion-migrate-worklogs.sh"
  "scripts/duration.py"
  "scripts/token-cost.py"
  "scripts/worklog-write.sh"
  "scripts/update-check.sh"
  "hooks/post-commit.sh"
  "hooks/stop.sh"
  "hooks/worklog.sh"
  "hooks/session-end.sh"
  "commands/finish.md"
  "commands/update-worklog.md"
  "commands/worklog.md"
  "commands/migrate-worklogs.md"
  "rules/auto-commit-rules.md"
  "rules/worklog-rules.md"
  "git-hooks/post-commit"
)

FAILED=0
for file in "${FILES[@]}"; do
  dst="$AI_WORKLOG_DIR/$file"
  [ -f "$dst" ] || continue  # 설치 안 된 파일은 스킵

  tmp=$(mktemp)
  if curl -sf --max-time 10 "$RAW_BASE/$file" -o "$tmp" 2>/dev/null; then
    mv "$tmp" "$dst"
    chmod +x "$dst" 2>/dev/null || true
  else
    rm -f "$tmp"
    FAILED=$(( FAILED + 1 ))
  fi
done

if [ "$FAILED" -gt 0 ]; then
  echo "worklog-for-claude: 업데이트 일부 실패 ($FAILED개). 다음 실행 시 재시도합니다." >&2
  exit 0
fi

# ── 버전 파일 갱신 ───────────────────────────────────────────────────────────
echo "$LATEST_SHA" > "$VERSION_FILE"

echo "worklog-for-claude $INSTALLED_SHA → $LATEST_SHA 업데이트 완료"
