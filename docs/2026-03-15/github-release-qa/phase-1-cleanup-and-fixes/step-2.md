# Step 2: Code Fixes

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | update-check.sh 레포 URL | `REPO="kangraemin/worklog-for-claude"` | ✅ |
| TC-02 | install.sh 완료 메시지 | "worklog-for-claude" 포함 | ✅ |
| TC-03 | worklog-write.sh 타임존 | `+09:00` 하드코딩 제거, `%z` 사용 | ✅ |
| TC-04 | duration.py 전체 JSONL 합산 | `find_latest_jsonl` 제거, glob 패턴으로 전체 처리 | ✅ |
| TC-05 | 기존 테스트 통과 | `python3 -m pytest tests/ -v` 전체 통과 | ✅ |

## 실행출력

TC-01: `grep 'REPO=' scripts/update-check.sh`
→ REPO="kangraemin/worklog-for-claude"

TC-02: `grep 'worklog-for-claude' install.sh | grep '설치'`
→ ok "$(t 'worklog-for-claude 설치가 완료되었습니다!' 'worklog-for-claude installed successfully!')"

TC-03: `grep 'DATETIME=' scripts/worklog-write.sh`
→ DATETIME=$(date +%Y-%m-%dT%H:%M:00%z) — +09:00 제거됨

TC-04: `grep 'find_latest_jsonl' scripts/duration.py`
→ 결과 없음 (함수 제거됨). glob.glob 패턴으로 전체 JSONL 합산

TC-05: `python3 -m pytest tests/ -v`
→ 176 passed in 48.82s
