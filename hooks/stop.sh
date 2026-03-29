#!/bin/bash
# Stop hook: WORKLOG_TIMING=stop이면 /worklog 스킬 실행 요청

# --- worklog-for-claude start ---
# WORKLOG_TIMING=manual이면 스킵
[ "${WORKLOG_TIMING:-stop}" = "manual" ] && exit 0

# jq 없으면 스킵
command -v jq &>/dev/null || exit 0

jq -n '{"additionalContext": "지금 /worklog 스킬을 실행해서 이번 세션의 작업 내용을 워크로그로 기록하세요."}'
# --- worklog-for-claude end ---
