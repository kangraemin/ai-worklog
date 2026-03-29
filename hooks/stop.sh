#!/bin/bash
# Stop hook: WORKLOG_TIMING=stop이면 /worklog 실행 요청

# jq 필수
command -v jq &>/dev/null || exit 0

INPUT=$(cat)

# --- worklog-for-claude start ---
# WORKLOG_TIMING=manual이면 스킵
[ "${WORKLOG_TIMING:-stop}" = "manual" ] && exit 0

# 재진입 방지: 이미 stop hook 처리 중이면 통과
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
[ "$STOP_HOOK_ACTIVE" = "true" ] && exit 0

jq -n '{
  "decision": "block",
  "reason": "/worklog 스킬을 실행해서 이번 세션의 작업 내용을 워크로그로 기록해줘."
}'
# --- worklog-for-claude end ---
