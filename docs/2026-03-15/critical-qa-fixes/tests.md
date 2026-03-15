| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | post-commit.sh에서 eval 코드 제거 | `grep -c 'eval' hooks/post-commit.sh` → 주석만 1건 (코드 0건) | ✅ |
| TC-02 | post-commit.sh bash 구문 유효 | `bash -n hooks/post-commit.sh` → exit 0 | ✅ |
| TC-03 | post-commit.sh settings.json env 로드 정상 동작 | 기존 E2E 테스트 통과 | ✅ |
| TC-04 | update-check.sh bootstrap에 mktemp 에러 처리 | mktemp 실패 시 exit 0 (에러 메시지 출력) | ✅ |
| TC-05 | update-check.sh 빈 파일 다운로드 차단 | `[ -s ]` 검증으로 빈 파일 거부 | ✅ |
| TC-06 | update-check.sh .sh 파일 구문 검증 | `bash -n` 실패 시 교체하지 않음 | ✅ |
| TC-07 | update-check.sh bash 구문 유효 | `bash -n scripts/update-check.sh` → exit 0 | ✅ |
| TC-08 | 기존 E2E 테스트 전체 통과 | pytest 전체 통과 | ✅ |

## 실행출력

TC-01: `grep -c 'eval' hooks/post-commit.sh`
→ 1 (주석 "eval 없이 안전하게 로드"만 매칭, 실제 eval 코드 없음)

TC-02: `bash -n hooks/post-commit.sh`
→ OK (exit 0)

TC-03: `python3 -m pytest tests/test_post_commit_e2e.py -x -q`
→ 26 passed in 11.38s

TC-04: 코드 확인 — `SELF_TMP=$(mktemp) || { echo "worklog-for-claude: mktemp failed" >&2; exit 0; }` (라인 78)

TC-05: 코드 확인 — `[ -s "$SELF_TMP" ]` (라인 82), `[ -s "$tmp" ]` (라인 134)

TC-06: 코드 확인 — `bash -n "$SELF_TMP"` (라인 82), `bash -n "$tmp"` (라인 136)

TC-07: `bash -n scripts/update-check.sh`
→ OK (exit 0)

TC-08: `python3 -m pytest tests/ -x -q`
→ 176 passed in 46.17s
