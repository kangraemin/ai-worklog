# Phase 1 Step 1: README.md 4개 항목 수정

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | jq optional 표기 | `jq` 행에 `*(optional)*` 포함 | ✅ |
| TC-02 | --delete-after 옵션 | `/migrate-worklogs --all --delete-after` 행 존재 | ✅ |
| TC-03 | FAQ background 표현 | "pending marker" 문구 포함, "in the background" 문구 없음 | ✅ |
| TC-04 | SessionStart 자동 업데이트 | "Automatic version check on session start" 문구 포함 | ✅ |

## 실행출력

TC-01: `grep -n 'optional' README.md`
→ `87:| \`jq\` *(optional)* | JSON processing (session cleanup) |`

TC-02: `grep -n 'delete-after' README.md`
→ `167:/migrate-worklogs --all --delete-after  # migrate and delete source files`

TC-03: `grep -n 'pending marker' README.md && grep -n 'in the background' README.md`
→ `305:Inside a Claude Code session, the hook writes a pending marker and exits immediately...` / "in the background" 매치 없음

TC-04: `grep -n 'Automatic version check on session start' README.md`
→ `72:- **Self-updating** — Automatic version check on session start, or manual with \`/update-worklog\`.`
