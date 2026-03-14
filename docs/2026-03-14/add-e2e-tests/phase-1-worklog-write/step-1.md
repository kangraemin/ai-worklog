# Step 1: Base 클래스 + NotionOnly + NotionBoth

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | notion-only 모드에서 로컬 파일 미생성 | `.worklogs/*.md` 없음 | ✅ |
| TC-02 | notion-only 모드에서 notion stub 호출됨 | stub 로그 파일 존재 | ✅ |
| TC-03 | notion-only 모드에서 stub에 올바른 인자 전달 | TITLE/DATE/PROJECT 비어있지 않음 | ✅ |
| TC-04 | notion 모드에서 로컬 파일 생성됨 | `.worklogs/*.md` 존재 | ✅ |
| TC-05 | notion 모드에서 notion stub 호출됨 | stub 로그 파일 존재 | ✅ |
| TC-06 | notion 모드에서 로컬 파일에 요약 텍스트 포함 | 요약 내용 포함 | ✅ |
| TC-07 | notion 모드에서 stub에 프로젝트명 전달 | `PROJECT=repo` | ✅ |
| TC-08 | notion-only 모드 정상 종료 | exit 0 | ✅ |
| TC-09 | pending 마커 정리 | pending JSON 삭제됨 | ✅ |

## 실행출력

TC-01~09: `python3 -m pytest tests/test_worklog_write_e2e.py -v`
→ 9 passed in 4.32s (전체 통과)

```
tests/test_worklog_write_e2e.py::TestNotionOnlyNoLocalFile::test_exit_zero PASSED
tests/test_worklog_write_e2e.py::TestNotionOnlyNoLocalFile::test_no_local_file_created PASSED
tests/test_worklog_write_e2e.py::TestNotionOnlyNoLocalFile::test_notion_stub_called PASSED
tests/test_worklog_write_e2e.py::TestNotionOnlyNoLocalFile::test_notion_stub_receives_correct_args PASSED
tests/test_worklog_write_e2e.py::TestNotionOnlyNoLocalFile::test_pending_cleaned PASSED
tests/test_worklog_write_e2e.py::TestNotionBothMode::test_local_content_has_summary PASSED
tests/test_worklog_write_e2e.py::TestNotionBothMode::test_local_file_created PASSED
tests/test_worklog_write_e2e.py::TestNotionBothMode::test_notion_stub_called PASSED
tests/test_worklog_write_e2e.py::TestNotionBothMode::test_stub_receives_project_name PASSED
```
