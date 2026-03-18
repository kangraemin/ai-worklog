# QA Check Report

> 점검일: 2026-03-18
> 프로젝트: worklog-for-claude
> 스택: Bash Shell Scripts, Python

## 요약

| 카테고리 | Critical | Important | Minor |
|----------|----------|-----------|-------|
| 코드 로직 | 0 | 2 | 4 |
| 보안 | 2 | 1 | 1 |
| 설정/환경 | 0 | 1 | 2 |
| 의존성 | 0 | 1 | 1 |
| 코드 품질 | 0 | 1 | 5 |
| **합계** | **2** | **6** | **13** |

---

## Critical 이슈

### [C-1] Shell Injection: PARENT_ID in install.sh
- **파일**: `install.sh:200, 219`
- **문제**: Python 인라인 코드에 `$PARENT_ID`를 shell 문자열 보간으로 삽입. 값에 `'` 또는 `"` 포함 시 JSON payload 깨짐 또는 주입 가능
  ```bash
  'page_id': '$PARENT_ID'   # ← 미이스케이프
  ```
- **영향**: Notion API 호출 실패 또는 payload 오염
- **수정 제안**: `json.dumps(os.environ['PARENT_ID'])` 방식으로 Python에서 안전하게 인코딩

### [C-2] Shell Injection: PARENT_PAGE_ID in notion-create-db.sh
- **파일**: `scripts/notion-create-db.sh:30`
- **문제**: `'page_id': '$PARENT_PAGE_ID'` — C-1과 동일 패턴
- **수정 제안**: 동일하게 Python json 모듈 사용

---

## Important 이슈

### [I-1] eval 패턴 (worklog-write.sh)
- **파일**: `scripts/worklog-write.sh:63`
- **문제**: `eval "$($PYTHON -c "..." 2>/dev/null || true)"` — Python 출력을 eval로 실행. Python 출력이 `export KEY=VALUE` 형식으로 제한되어 있어 위험도는 낮지만, 안전하지 않은 패턴
- **수정 제안**: `source <(python ...)` 또는 변수를 명시적으로 파싱

### [I-2] 스냅샷 파일 Race Condition
- **파일**: `scripts/worklog-write.sh:90-94, 206-207`
- **문제**: `~/.claude/worklogs/.snapshot` 파일을 read/write 시 파일 락 없음. 동시에 두 세션에서 `/worklog` 실행 시 타임스탬프 유실 가능
- **수정 제안**: `flock` 또는 임시파일 + atomic rename 패턴 사용

### [I-3] Notion 오류가 2>/dev/null로 묻힘
- **파일**: `scripts/worklog-write.sh:201`
- **문제**: `2>/dev/null && echo "✓" || echo "✗" >&2` — 실패 메시지는 출력되지만 실제 오류 원인은 소거됨
- **수정 제안**: stderr를 임시파일로 캡처 후 실패 시 보여주기

### [I-4] 하드코딩된 Claude API 가격 (stale 위험)
- **파일**: `scripts/token-cost.py:23-42`
- **문제**: 가격이 하드코딩되어 있음. Anthropic이 가격을 변경하면 계산이 부정확해지지만 아무런 경고가 없음
- **수정 제안**: 파일 상단에 마지막 업데이트 날짜 주석 추가. 현재 기준으로 최신 모델(claude-sonnet-4-6 등) 가격 확인 필요

### [I-5] Python 실행파일 매번 재탐색
- **파일**: `install.sh:50-56`, `worklog-write.sh:20`, `post-commit.sh:42`, `update-check.sh:9`
- **문제**: `command -v python3 || command -v python || echo python3` 패턴이 스크립트마다 반복됨. install 시 한 번 확인하고 settings.json에 저장하는 게 맞음
- **수정 제안**: install 시 탐지한 Python 경로를 `settings.json` env에 `PYTHON_CMD`로 저장

### [I-6] post-commit.sh에서 파일 경로 불안전 삽입
- **파일**: `hooks/post-commit.sh:49-56`
- **문제**: `$LOCAL_SETTINGS` 경로가 Python 인라인 코드에 단따옴표로 둘러싸인 문자열로 직접 삽입됨. 경로에 `'` 포함 시 Python 파싱 오류
- **수정 제안**: 환경변수로 전달하고 Python에서 `os.environ` 사용

---

## Minor 이슈

### [M-1] COMMIT_MSG 특수문자 미이스케이프
- **파일**: `hooks/post-commit.sh:100-137`
- **문제**: 커밋 메시지에 `"` 또는 `\` 포함 시 PROMPT 문자열 오염 가능
- **수정 제안**: `printf '%s' "$COMMIT_MSG"` 또는 heredoc으로 전달

### [M-2] .collecting 디렉토리 고아 파일 누적
- **파일**: `hooks/session-end.sh:11-13`, `hooks/worklog.sh:26`
- **문제**: 세션이 비정상 종료되면 `.collecting/$SESSION_ID.jsonl` 파일이 정리되지 않고 누적됨
- **수정 제안**: update-check나 install 시 일정 기간 이상 된 `.collecting/*.jsonl` 자동 정리

### [M-3] 미사용 변수 CHANGED_FILES
- **파일**: `scripts/worklog-write.sh:122`
- **문제**: `CHANGED_FILES=$(git diff HEAD~1 ...)` 계산 후 사용 안 됨 — 데드 코드
- **수정 제안**: 삭제

### [M-4] git 의존성 체크 누락
- **파일**: `install.sh:428`, `hooks/post-commit.sh:17`
- **문제**: `git` 명령이 있다고 가정하고 실행. 오류 메시지가 모호해질 수 있음
- **수정 제안**: 스크립트 상단에 `command -v git >/dev/null || { echo "git required"; exit 1; }`

### [M-5] Notion 토큰 curl 에러 출력에 노출 가능성
- **파일**: `scripts/notion-worklog.sh:114, 123`
- **문제**: curl verbose 에러 시 Authorization 헤더가 출력될 수 있음 (`-s` 플래그로 대부분 억제되지만 완전하지 않음)
- **수정 제안**: `--no-progress-meter`와 함께 에러 로그를 별도 파일로 리다이렉트

### [M-6] token-cost.py 부동소수점 반올림
- **파일**: `scripts/token-cost.py:66-71`
- **문제**: 부동소수점 연산으로 $0.001 미만 오차 가능. 실사용에서 무시 가능 수준
- **수정 제안**: `decimal.Decimal` 사용 (선택)

### [M-7] update-check.sh trap 정리 불완전
- **파일**: `scripts/update-check.sh:78-95`
- **문제**: `trap - EXIT` 전에 오류 발생 시 임시파일 미삭제 가능성. 단, 명시적 `rm -f` 호출로 대부분 커버됨
- **수정 제안**: `trap 'rm -f "$SELF_TMP"; trap - EXIT' EXIT`로 통합

---

## TODO/FIXME 목록

특별히 발견된 TODO/FIXME 주석 없음.

---

## 점검하지 않은 영역

- Notion API 응답 스키마 변경 대응 (외부 서비스)
- Claude API 스키마 변경 (post-commit.sh의 claude -p 호출)
- install.sh의 전체 설치 플로우 E2E (테스트로 커버 여부 미확인)
- `tests/` 디렉토리 내 E2E 테스트 코드 자체의 품질

---

## 결론

배포 블로커: **C-1, C-2** (Notion PARENT_ID 주입 — 특수문자 포함 ID 사용 시 API 호출 실패)

일반적인 영문/숫자 Notion 페이지 ID 사용 시 C-1/C-2는 실제 트리거되지 않을 가능성이 높음.
실운용 환경에서 문제 발생 빈도 낮음 → **조건부 배포 가능** (단, I-4 가격 데이터 확인 권장).
