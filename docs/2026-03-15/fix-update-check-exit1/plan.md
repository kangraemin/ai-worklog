# fix: update-check.sh exit 1 버그 수정

## 변경 파일별 상세

### `scripts/update-check.sh`

- **변경 이유**: `set -euo pipefail` 환경에서 `_register_session_start` 함수 내 Python 호출 실패 시 exit 1 전파됨
- **Before** (line 186):
```bash
_register_session_start "$HOME/.claude/settings.json"
```
- **After**:
```bash
_register_session_start "$HOME/.claude/settings.json" || true
```
- **영향 범위**: SessionStart 등록 실패 시 무시하고 계속 진행. 버전 파일 갱신과 성공 메시지는 정상 출력.

## 검증

- 검증 명령어: `bash -n scripts/update-check.sh && AI_WORKLOG_DIR=~/.claude bash ~/.claude/scripts/update-check.sh --check-only`
- 기대 결과: exit 0, `installed/latest/status` 출력
