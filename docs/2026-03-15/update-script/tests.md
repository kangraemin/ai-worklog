| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | update-check.sh pretty output 로직 | 색상 변수, cmp -s 분기, UNCHANGED 카운터 존재 | ✅ |
| TC-02 | SessionStart hook 자동 등록 로직 | _register_session_start 함수 + SessionStart 키워드 존재 | ✅ |
| TC-03 | install.sh hook_defs SessionStart 포함 | SessionStart.*update-check.sh 행 존재 | ✅ |

## 실행출력

TC-01: `grep -c '_G=.*_D=.*_R=.*_B=.*_N=' scripts/update-check.sh && grep -c 'cmp -s' ... && grep -c 'UNCHANGED' ...`
→ 1, 1, 3 — PASS

TC-02: `grep -c '_register_session_start' scripts/update-check.sh && grep -c 'SessionStart' ...`
→ 2, 3 — PASS

TC-03: `grep -c "SessionStart.*update-check.sh" install.sh`
→ 1 — PASS

추가: `bash -n scripts/update-check.sh` → SYNTAX OK
