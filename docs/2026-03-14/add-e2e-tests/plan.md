# E2E 테스트 추가 — 9개 시나리오

## Context
기존 E2E(install.sh, post-commit)는 충실하나, worklog-write.sh의 DEST/LANG 분기, stop.sh 마커 감지, session-end.sh 정리, 에러 핸들링, 환경변수 조합 테스트가 없다. 이를 추가하여 커버리지를 높인다.

## 변경 파일별 상세

### `tests/test_worklog_write_e2e.py` (신규)
- **변경 이유**: worklog-write.sh의 WORKLOG_DEST/LANG/GIT_TRACK 분기를 실제 실행으로 검증
- **After**:
  - `_WorklogWriteBase`: tmpdir 격리 + git repo + notion-worklog.sh stub
  - `TestNotionOnlyNoLocalFile`: DEST=notion-only → `.worklogs/` 파일 미생성, stub 호출됨
  - `TestNotionBothMode`: DEST=notion → 로컬 파일 + stub 호출
  - `TestEnglishOutput`: LANG=en → `### Token Usage`, `- Model:` 영어 헤더
  - `TestGitTrackFalse`: GIT_TRACK=false → 파일 존재하나 staged 안 됨

### `tests/test_hooks_e2e.py` (신규)
- **변경 이유**: stop.sh 마커 감지, session-end.sh 정리, 에러 핸들링 검증
- **After**:
  - `TestStopPendingMarker`: pending JSON → block + /worklog
  - `TestStopUncommittedChanges`: dirty repo → block + /finish
  - `TestSessionEndCleanup`: collecting JSONL 삭제
  - `TestPostCommitMissingAiDir`: AI_WORKLOG_DIR 없어도 exit 0

### `tests/test_env_combinations_e2e.py` (신규)
- **변경 이유**: TIMING × DEST 크로스 조합 검증
- **After**:
  - `TestTimingDestCombinations`: manual=스킵, stop=DEST별 동작

## 검증
- 검증 명령어: `python3 -m pytest tests/test_worklog_write_e2e.py tests/test_hooks_e2e.py tests/test_env_combinations_e2e.py -v`
- 기대 결과: 약 27개 테스트 전부 통과
