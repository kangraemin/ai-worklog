# WORKLOG_TIMING: each-commit → stop 리네이밍

## 변경 파일별 상세

### `hooks/post-commit.sh` (line 5-7)
- **변경 이유**: 기본값 `each-commit` → `stop`
- **Before**:
```bash
# ── WORKLOG_TIMING 체크 ──────────────────────────────────────────────────────
# manual이면 스킵 (each-commit이 기본)
[ "${WORKLOG_TIMING:-each-commit}" = "manual" ] && exit 0
```
- **After**:
```bash
# ── WORKLOG_TIMING 체크 ──────────────────────────────────────────────────────
# manual이면 스킵 (stop이 기본)
[ "${WORKLOG_TIMING:-stop}" = "manual" ] && exit 0
```

### `hooks/worklog.sh` (line 10-11)
- **변경 이유**: 기본값 `each-commit` → `stop`
- **Before**:
```bash
# WORKLOG_TIMING=manual이면 수집 불필요
[ "${WORKLOG_TIMING:-each-commit}" = "manual" ] && exit 0
```
- **After**:
```bash
# WORKLOG_TIMING=manual이면 수집 불필요
[ "${WORKLOG_TIMING:-stop}" = "manual" ] && exit 0
```

### `install.sh` (line 273-286, 291)
- **변경 이유**: 선택지 텍스트 + 변수값 + 조건 변경
- **Before**:
```bash
echo "  1) each-commit — $(t '커밋할 때마다 자동 (추천)' 'automatically on each commit (recommended)')"
echo "  2) manual      — $(t '/worklog 실행할 때만' 'only when running /worklog')"
...
  *) WORKLOG_TIMING="each-commit" ;;
...
if [ "$WORKLOG_TIMING" = "each-commit" ]; then
```
- **After**:
```bash
echo "  1) stop   — $(t '대화 종료 시 자동 (추천)' 'automatically on session end (recommended)')"
echo "  2) manual — $(t '/worklog 실행할 때만' 'only when running /worklog')"
...
  *) WORKLOG_TIMING="stop" ;;
...
if [ "$WORKLOG_TIMING" = "stop" ]; then
```

### `rules/worklog-rules.md`
- **Before**: `each-commit` | git post-commit hook이 커밋마다 자동 작성 (기본)
- **After**: `stop` | 대화 종료 시 자동 작성 (기본)
- 모드 체크 섹션도 갱신

### `README.md` (line 151, 185)
- WORKLOG_TIMING 테이블 행 업데이트
- "Works regardless of" 문구 정리

### `tests/test_post_commit_e2e.py`
- `WORKLOG_TIMING: "each-commit"` → `WORKLOG_TIMING: "stop"`

### `tests/test_install_e2e.py`
- `assertEqual(env["WORKLOG_TIMING"], "each-commit")` → `"stop"`

## 검증
- `python3 -m pytest tests/test_post_commit_e2e.py -v`
- `python3 -m pytest tests/test_install_e2e.py -v`
- `grep -rn 'each-commit' .` 잔여 참조 없는지 확인
