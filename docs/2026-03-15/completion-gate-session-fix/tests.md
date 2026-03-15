| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | collecting 파일 없는 세션 → dirty check 스킵 | exit 0 (블로킹 없음) | ✅ |
| TC-02 | collecting에 Read/Grep만 있는 세션 → dirty check 스킵 | exit 0 (블로킹 없음) | ✅ |
| TC-03 | collecting에 Write 있는 세션 + dirty repo → 블로킹 | decision: block 출력 | ✅ |

## 실행출력

TC-01: `echo '{"session_id":"test-no-collect","stop_hook_active":false,"cwd":"/tmp"}' | bash ~/.claude/hooks/stop.sh; echo "EXIT=$?"`
→ EXIT=0 (블로킹 없음)

TC-02: collecting에 Read/Grep/Glob만 기록 후 실행
→ EXIT=0 (블로킹 없음)

TC-03: collecting에 Write 기록 + dirty git repo에서 실행
→ `{"decision":"block","reason":"/finish 스킬을 실행해서 커밋, 푸시, 워크로그를 작성해줘."}` (기존 동작 유지)
