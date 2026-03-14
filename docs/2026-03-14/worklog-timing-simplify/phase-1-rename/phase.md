# Phase 1: each-commit → stop 리네이밍

## 목표
WORKLOG_TIMING 환경변수의 `each-commit` 값을 `stop`으로 전체 리네이밍

## 범위
- 셸 스크립트: `hooks/post-commit.sh`, `hooks/worklog.sh`, `install.sh`
- 문서: `rules/worklog-rules.md`, `README.md`
- 테스트: `tests/test_post_commit_e2e.py`, `tests/test_install_e2e.py`
- 글로벌 룰: `~/.claude/rules/worklog-rules.md`

## Steps
1. 셸 스크립트 수정 (hooks/post-commit.sh, hooks/worklog.sh, install.sh)
2. 문서 수정 (rules/worklog-rules.md, README.md, ~/.claude/rules/worklog-rules.md)
3. 테스트 수정 (tests/test_post_commit_e2e.py, tests/test_install_e2e.py)
4. 잔여 참조 검증 (grep -rn 'each-commit' 결과 0건 확인)
