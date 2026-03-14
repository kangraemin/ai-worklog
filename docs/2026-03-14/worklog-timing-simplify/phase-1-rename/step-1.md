# Step 1: 셸 스크립트 수정

## 대상 파일
- `hooks/post-commit.sh`
- `hooks/worklog.sh`
- `install.sh`

## TC

| TC | 설명 | 검증 방법 | 판정 |
|----|------|-----------|------|
| TC-1 | post-commit.sh에 `each-commit` 문자열 없음 | `grep -c 'each-commit' hooks/post-commit.sh` → 0 | ✅ |
| TC-2 | post-commit.sh에 `stop` 기본값 존재 | `grep -c 'WORKLOG_TIMING:-stop' hooks/post-commit.sh` → 1 | ✅ |
| TC-3 | worklog.sh에 `each-commit` 문자열 없음 | `grep -c 'each-commit' hooks/worklog.sh` → 0 | ✅ |
| TC-4 | worklog.sh에 `stop` 기본값 존재 | `grep -c 'WORKLOG_TIMING:-stop' hooks/worklog.sh` → 1 | ✅ |
| TC-5 | install.sh에 `each-commit` 문자열 없음 | `grep -c 'each-commit' install.sh` → 0 | ✅ |
| TC-6 | install.sh에 `stop` 기본값/선택지 존재 | `grep -c 'stop' install.sh` → 3 이상 | ✅ (17) |

## 실행출력
```
TC-1: 0
TC-2: 1
TC-3: 0
TC-4: 1
TC-5: 0
TC-6: 17
```
