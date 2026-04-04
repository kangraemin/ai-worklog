#!/bin/bash
# PostToolUse(Bash) hook: git commit 감지 → PROJECT.md 자동 생성/업데이트

set -euo pipefail

# git commit 명령어가 아니면 스킵
command -v jq &>/dev/null || exit 0
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')
printf '%s' "$COMMAND" | grep -qE '(^|\n|;|&&|\|\|)\s*git\s+commit(\s|$)' || exit 0

# CWD 확보
CWD=$(echo "$INPUT" | jq -r '.cwd // ""')
[ -z "$CWD" ] && CWD="$(pwd)"
cd "$CWD" 2>/dev/null || exit 0

# git repo 아니면 스킵
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
    exit 0
fi

THRESHOLD="${PROJECT_DOC_CHECK_INTERVAL:-5}"

# PROJECT.md 마지막 수정 커밋 hash (없으면 전체 커밋 수 사용)
LAST_HASH=$(git log -1 --format="%H" -- PROJECT.md 2>/dev/null || echo "")

if [ -z "$LAST_HASH" ]; then
    COMMITS_SINCE=$(git log --oneline 2>/dev/null | wc -l | tr -d ' ')
else
    COMMITS_SINCE=$(git log --oneline "${LAST_HASH}..HEAD" 2>/dev/null | wc -l | tr -d ' ')
fi

if [ "$COMMITS_SINCE" -ge "$THRESHOLD" ]; then
    # 별도 프로세스로 claude -p 실행 (현재 세션 블로킹 안 함)
    nohup claude -p "PROJECT.md를 /update-project 스킬 기준으로 생성 또는 업데이트해. 사용자 확인 없이 바로 반영해." \
        --model sonnet \
        --cwd "$CWD" \
        > /tmp/commit-doc-check.log 2>&1 &
fi
