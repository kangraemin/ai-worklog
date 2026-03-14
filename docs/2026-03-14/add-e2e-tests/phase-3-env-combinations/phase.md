# Phase 3: 환경변수 조합 E2E 테스트

## 목표
WORKLOG_TIMING × WORKLOG_DEST 크로스 조합을 실제 post-commit.sh 실행으로 검증

## 범위
- `tests/test_env_combinations_e2e.py` 신규 생성
- 1개 테스트 클래스: TestTimingDestCombinations (6개 테스트)

## Steps
1. `_EnvComboBase` + `TestTimingDestCombinations` 전체 구현 + 검증
