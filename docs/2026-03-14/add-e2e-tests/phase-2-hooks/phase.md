# Phase 2: Hooks E2E 테스트

## 목표
stop.sh, session-end.sh, post-commit.sh의 에러 핸들링을 실제 실행으로 검증

## 범위
- `tests/test_hooks_e2e.py` 신규 생성
- 4개 테스트 클래스: StopPending, StopUncommitted, SessionEnd, MissingAiDir

## Steps
1. `_HookBase` + `TestStopPendingMarker` + `TestStopUncommittedChanges` 구현
2. `TestSessionEndCleanup` + `TestPostCommitMissingAiDir` 구현 + Phase 2 전체 검증
