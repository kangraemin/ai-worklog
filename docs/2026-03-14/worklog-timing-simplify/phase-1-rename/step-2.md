# Step 2: 문서 수정

## 대상 파일
- `rules/worklog-rules.md` (프로젝트)
- `~/.claude/rules/worklog-rules.md` (글로벌)
- `README.md`

## TC

| TC | 설명 | 검증 방법 | 판정 |
|----|------|-----------|------|
| TC-1 | rules/worklog-rules.md에 `each-commit` 없음 | `grep -c 'each-commit' rules/worklog-rules.md` → 0 | ✅ |
| TC-2 | rules/worklog-rules.md에 `stop` 기본값 존재 | `grep -c 'stop' rules/worklog-rules.md` → 2 이상 | ✅ (2) |
| TC-3 | README.md에 `each-commit` 없음 | `grep -c 'each-commit' README.md` → 0 | ✅ |
| TC-4 | README.md에 `stop` 값 존재 | `grep -c 'stop' README.md` → 2 이상 | ✅ (4) |
| TC-5 | ~/.claude/rules/worklog-rules.md에 `each-commit` 없음 | `grep -c 'each-commit' ~/.claude/rules/worklog-rules.md` → 0 | ✅ |

## 실행출력
```
TC-1: 0
TC-2: 2
TC-3: 0
TC-4: 4
TC-5: 0
```
