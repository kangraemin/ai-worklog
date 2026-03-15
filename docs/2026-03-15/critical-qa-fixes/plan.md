# Critical QA 이슈 2건 수정

## Context
QA 점검에서 발견된 Critical 2건을 수정한다:
- C-1: `hooks/post-commit.sh`에서 `eval`로 settings.json env를 로드 — 명령 주입 위험
- C-2: `scripts/update-check.sh`에서 다운로드 스크립트 무결성 검증 없이 교체

## 변경 파일별 상세

### `hooks/post-commit.sh`
- **변경 이유**: `eval "$(...)"` 패턴이 settings.json의 env 값을 셸 명령으로 실행. 악의적 값 포함 시 임의 명령 실행 가능.
- **Before** (라인 71-81):
```bash
SETTINGS_FILE="$AI_WORKLOG_DIR/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
  eval "$($PYTHON -c "
import json, sys
try:
    cfg = json.load(open('$SETTINGS_FILE'))
    for k, v in cfg.get('env', {}).items():
        print(f'export {k}=\"{v}\"')
except:
    pass
" 2>/dev/null || true)"
fi
```
- **After**:
```bash
SETTINGS_FILE="$AI_WORKLOG_DIR/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
  while IFS='=' read -r key value; do
    [ -n "$key" ] && export "$key=$value"
  done < <($PYTHON -c "
import json, sys, os
try:
    cfg = json.load(open(os.environ.get('_SETTINGS_PATH', '')))
    for k, v in cfg.get('env', {}).items():
        print(f'{k}={v}')
except:
    pass
" 2>/dev/null <<< "" || true)
fi
```
핵심 변경: `eval` 제거 → `while read` + `export "$key=$value"` 패턴. `export`의 인자를 하나의 문자열로 전달하면 셸 메타문자가 해석되지 않음. Python에도 `$SETTINGS_FILE` 직접 보간 대신 환경변수로 전달.

### `scripts/update-check.sh`
- **변경 이유**: 다운로드 스크립트를 검증 없이 `mv` + `chmod +x` + `exec`로 즉시 실행. 잘린 파일이나 변조된 파일이 실행될 수 있음. mktemp 실패 시 빈 경로로 파일 연산.
- **변경 범위**: bootstrap 섹션(77-90) + 파일 다운로드 루프(121-136)

**변경 1: bootstrap 섹션 (라인 77-90)**
- **Before**:
```bash
if [ "${_UPDATE_BOOTSTRAPPED:-}" != "1" ]; then
  SELF_TMP=$(mktemp)
  if curl -sf --max-time 10 "$RAW_BASE/scripts/update-check.sh" -o "$SELF_TMP" 2>/dev/null; then
    if ! cmp -s "$SELF_TMP" "$SELF_SCRIPT"; then
      mv "$SELF_TMP" "$SELF_SCRIPT"
      chmod +x "$SELF_SCRIPT"
      export _UPDATE_BOOTSTRAPPED=1
      exec bash "$SELF_SCRIPT" --force
    fi
    rm -f "$SELF_TMP"
  else
    rm -f "$SELF_TMP"
  fi
fi
```
- **After**:
```bash
if [ "${_UPDATE_BOOTSTRAPPED:-}" != "1" ]; then
  SELF_TMP=$(mktemp) || { echo "worklog-for-claude: mktemp failed" >&2; exit 0; }
  trap 'rm -f "$SELF_TMP"' EXIT
  if curl -sf --max-time 10 "$RAW_BASE/scripts/update-check.sh" -o "$SELF_TMP" 2>/dev/null; then
    # 무결성 검증: 비어있지 않고, 유효한 bash 구문이어야 함
    if [ -s "$SELF_TMP" ] && bash -n "$SELF_TMP" 2>/dev/null; then
      if ! cmp -s "$SELF_TMP" "$SELF_SCRIPT"; then
        mv "$SELF_TMP" "$SELF_SCRIPT"
        chmod +x "$SELF_SCRIPT"
        trap - EXIT
        export _UPDATE_BOOTSTRAPPED=1
        exec bash "$SELF_SCRIPT" --force
      fi
    else
      echo "worklog-for-claude: 다운로드 파일 검증 실패, 업데이트 건너뜀" >&2
    fi
  fi
  rm -f "$SELF_TMP"
  trap - EXIT
fi
```
핵심 변경: (1) mktemp 실패 처리, (2) `trap`으로 임시 파일 정리 보장, (3) `[ -s ] && bash -n`으로 비어있거나 깨진 스크립트 차단.

**변경 2: 파일 다운로드 루프 (라인 121-136)**
- **Before**:
```bash
  tmp=$(mktemp)
  if curl -sf --max-time 10 "$RAW_BASE/$file" -o "$tmp" 2>/dev/null; then
    mv "$tmp" "$dst"
    chmod +x "$dst" 2>/dev/null || true
    UPDATED=$(( UPDATED + 1 ))
  else
    rm -f "$tmp"
    FAILED=$(( FAILED + 1 ))
  fi
```
- **After**:
```bash
  tmp=$(mktemp) || { FAILED=$(( FAILED + 1 )); continue; }
  if curl -sf --max-time 10 "$RAW_BASE/$file" -o "$tmp" 2>/dev/null && [ -s "$tmp" ]; then
    # .sh 파일이면 bash 구문 검증
    if [[ "$file" == *.sh ]] && ! bash -n "$tmp" 2>/dev/null; then
      rm -f "$tmp"
      FAILED=$(( FAILED + 1 ))
      continue
    fi
    mv "$tmp" "$dst"
    chmod +x "$dst" 2>/dev/null || true
    UPDATED=$(( UPDATED + 1 ))
  else
    rm -f "$tmp"
    FAILED=$(( FAILED + 1 ))
  fi
```
핵심 변경: (1) mktemp 실패 처리, (2) 빈 파일 차단 `[ -s ]`, (3) .sh 파일은 `bash -n` 구문 검증.

## 검증
- `bash -n hooks/post-commit.sh` — 문법 검증
- `bash -n scripts/update-check.sh` — 문법 검증
- 기존 테스트: `python3 -m pytest tests/test_post_commit_e2e.py -x -q`
- 기존 테스트: `python3 -m pytest tests/test_hooks_e2e.py -x -q`
