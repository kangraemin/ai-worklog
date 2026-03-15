# TC: fix-update-check-exit1

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | `--check-only` 실행 시 exit 0 | exit 0 | ✅ |
| TC-02 | bash -n 구문 검증 통과 | exit 0 | ✅ |
| TC-03 | line 186에 `|| true` 추가 확인 | grep으로 확인 | ✅ |

## 실행출력

TC-01: `AI_WORKLOG_DIR=~/.claude bash ~/.claude/scripts/update-check.sh --check-only; echo "exit: $?"`
→ exit: 0 (24h throttle로 출력 없음, 정상)

TC-02: `bash -n scripts/update-check.sh && echo "TC-02: exit $?"`
→ TC-02: exit 0

TC-03: `grep -n "|| true" scripts/update-check.sh`
→ 151: chmod +x "$dst" 2>/dev/null || true
→ 186: _register_session_start "$HOME/.claude/settings.json" || true
