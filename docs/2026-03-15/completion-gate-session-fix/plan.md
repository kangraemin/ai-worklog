# stop.sh 세션 격리 수정

## 변경 파일별 상세

### `~/.claude/hooks/stop.sh`
- **변경 이유**: 파일 수정 도구를 사용하지 않은 세션은 git dirty 체크 스킵
- **Before** (29-36줄):
```bash
INPUT=$(cat)
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')

# 재진입 방지: 이미 stop hook으로 계속 진행 중이면 통과
[ "$STOP_HOOK_ACTIVE" = "true" ] && exit 0

CWD=$(echo "$INPUT" | jq -r '.cwd')
cd "$CWD" 2>/dev/null || exit 0
```
- **After**:
```bash
INPUT=$(cat)
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')

# 재진입 방지: 이미 stop hook으로 계속 진행 중이면 통과
[ "$STOP_HOOK_ACTIVE" = "true" ] && exit 0

# 세션 격리: 파일 수정 도구를 사용하지 않은 세션은 dirty check 스킵
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // ""')
if [ -n "$SESSION_ID" ]; then
  COLLECT_FILE="$HOME/.claude/worklogs/.collecting/$SESSION_ID.jsonl"
  if [ ! -f "$COLLECT_FILE" ]; then
    exit 0
  fi
  HAS_MODIFYING=$(grep -cE '"tool":"(Write|Edit|MultiEdit|Bash|NotebookEdit)"' "$COLLECT_FILE" 2>/dev/null || echo 0)
  if [ "$HAS_MODIFYING" = "0" ]; then
    exit 0
  fi
fi

CWD=$(echo "$INPUT" | jq -r '.cwd')
cd "$CWD" 2>/dev/null || exit 0
```
- **영향 범위**: stop.sh를 사용하는 모든 프로젝트

## 검증
- 검증 명령어: `echo '{"session_id":"test-no-collect","cwd":"/tmp"}' | bash ~/.claude/hooks/stop.sh`
- 기대 결과: collecting 파일 없으므로 exit 0 (블로킹 없음)
