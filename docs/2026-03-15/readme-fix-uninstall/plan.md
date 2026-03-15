# README.md 수정 + uninstall.sh 생성

## Context

README.md 검증 결과 5개 부정확/누락 항목 발견. 실제 코드와 일치하도록 수정하고, README에 언급된 uninstall.sh를 생성한다.

## 변경 파일별 상세

### `README.md` — 4개 항목 수정

#### 1. Prerequisites: jq optional 표기 (line 87)

- **변경 이유**: jq는 session-end.sh에서만 선택적으로 사용 (없으면 조용히 스킵)
- **Before**:
```
| `jq` | JSON processing |
```
- **After**:
```
| `jq` *(optional)* | JSON processing (session cleanup) |
```

#### 2. /migrate-worklogs: --delete-after 옵션 추가 (line 163-167)

- **변경 이유**: notion-migrate-worklogs.sh에 --delete-after 옵션이 구현되어 있으나 README에 미기재
- **Before**:
```
/migrate-worklogs              # dry-run preview
/migrate-worklogs --all        # migrate all .md files
/migrate-worklogs --date 2026-03-01  # specific date only
```
- **After**:
```
/migrate-worklogs              # dry-run preview
/migrate-worklogs --all        # migrate all .md files
/migrate-worklogs --date 2026-03-01  # specific date only
/migrate-worklogs --all --delete-after  # migrate and delete source files
```

#### 3. FAQ: background 표현 수정 (line 303-305)

- **변경 이유**: 실제로는 동기 실행이며 background(&)로 실행하지 않음
- **Before**:
```
The post-commit hook runs `claude -p` in the background. Your commit completes immediately.
```
- **After**:
```
Inside a Claude Code session, the hook writes a pending marker and exits immediately — your commit is never blocked. Outside Claude Code, it runs `claude -p` synchronously but completes in seconds.
```

#### 4. Features: SessionStart 자동 업데이트 추가 (line 72)

- **변경 이유**: install.sh가 SessionStart hook에 update-check.sh를 등록하지만 README에 미언급
- **Before**:
```
- **Self-updating** — Built-in version check with `/update-worklog`.
```
- **After**:
```
- **Self-updating** — Automatic version check on session start, or manual with `/update-worklog`.
```

### `uninstall.sh` — 신규 생성

- **용도**: install.sh가 설치한 파일/설정을 안전하게 제거
- **제거 대상**:
  1. settings.json에서 worklog 관련 hooks 제거
  2. settings.json에서 WORKLOG_* env 변수 제거
  3. 설치된 파일 삭제 (scripts/, hooks/, commands/, rules/, git-hooks/)
  4. git config --global --unset core.hooksPath (전역 설치 시)
- **보존 대상**: .worklogs/, .env(NOTION_TOKEN)

## 검증

- `bash -n uninstall.sh` — 구문 오류 없는지
- README diff 확인: 4개 수정 포인트
- uninstall.sh 실행 가능 여부 (--help)
