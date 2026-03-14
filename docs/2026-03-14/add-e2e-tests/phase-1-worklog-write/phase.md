# Phase 1: worklog-write.sh E2E 테스트

## 목표
worklog-write.sh의 WORKLOG_DEST, WORKLOG_LANG, WORKLOG_GIT_TRACK 분기를 실제 실행으로 검증하는 E2E 테스트 작성

## 범위
- `tests/test_worklog_write_e2e.py` 신규 생성
- `_WorklogWriteBase` 클래스: tmpdir + git repo + notion stub
- 4개 테스트 클래스: NotionOnly, NotionBoth, EnglishOutput, GitTrackFalse

## Steps
1. `_WorklogWriteBase` + `TestNotionOnlyNoLocalFile` + `TestNotionBothMode` 구현
2. `TestEnglishOutput` + `TestGitTrackFalse` 구현 + Phase 1 전체 검증
