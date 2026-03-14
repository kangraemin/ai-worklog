# Step 1: TIMING × DEST 크로스 조합

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | manual + git → 스킵 | `.worklogs/` 없음 | ✅ |
| TC-02 | manual + notion → 스킵 | stub 미호출 | ✅ |
| TC-03 | manual + notion-only → 스킵 | stub 미호출 | ✅ |
| TC-04 | stop + git → 로컬 파일 생성 | `.worklogs/*.md` 존재 | ✅ |
| TC-05 | stop + notion → 로컬 + stub | 둘 다 존재 | ✅ |
| TC-06 | stop + notion-only → stub만 | 로컬 없음, stub 호출 | ✅ |

## 실행출력

TC-01~06: `python3 -m pytest tests/test_env_combinations_e2e.py -v`
→ 6 passed in 3.36s

```
tests/test_env_combinations_e2e.py::TestTimingDestCombinations::test_manual_git_skips PASSED
tests/test_env_combinations_e2e.py::TestTimingDestCombinations::test_manual_notion_only_skips PASSED
tests/test_env_combinations_e2e.py::TestTimingDestCombinations::test_manual_notion_skips PASSED
tests/test_env_combinations_e2e.py::TestTimingDestCombinations::test_stop_git_creates_local PASSED
tests/test_env_combinations_e2e.py::TestTimingDestCombinations::test_stop_notion_creates_both PASSED
tests/test_env_combinations_e2e.py::TestTimingDestCombinations::test_stop_notion_only_no_local PASSED
```
