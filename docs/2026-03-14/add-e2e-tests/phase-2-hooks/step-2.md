# Step 2: SessionEnd + MissingAiDir

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | session-end 후 collecting 파일 삭제 | 파일 없음 | ✅ |
| TC-02 | session-end 정상 종료 | exit 0 | ✅ |
| TC-03 | 존재하지 않는 session_id도 정상 | exit 0 | ✅ |
| TC-04 | AI_WORKLOG_DIR 누락 시 graceful exit | exit 0 | ✅ |
| TC-05 | AI_WORKLOG_DIR 누락 시 traceback 없음 | stderr에 Traceback 미포함 | ✅ |

## 실행출력

TC-01~05: `python3 -m pytest tests/test_hooks_e2e.py -v`
→ 11 passed in 2.72s (Phase 2 전체 통과)

```
tests/test_hooks_e2e.py::TestSessionEndCleanup::test_collecting_file_removed PASSED
tests/test_hooks_e2e.py::TestSessionEndCleanup::test_exit_zero PASSED
tests/test_hooks_e2e.py::TestSessionEndCleanup::test_nonexistent_session_ok PASSED
tests/test_hooks_e2e.py::TestPostCommitMissingAiDir::test_graceful_exit PASSED
tests/test_hooks_e2e.py::TestPostCommitMissingAiDir::test_no_traceback PASSED
```
