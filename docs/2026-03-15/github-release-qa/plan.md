# GitHub 릴리스 QA: worklog-for-claude

## Context

사용자가 이 프로젝트를 GitHub에서 바로 clone해서 쓸 수 있는 수준인지 품질 점검 요청.
코드 전체를 읽고 발견한 문제점을 정리하고, 수정 계획을 세운다.

---

## 평가 결과

### 잘 된 부분

- **install.sh** — 인터랙티브 위저드, 이중 언어, hook chaining, 사전 조건 체크 등 완성도 높음
- **핵심 스크립트** — worklog-write.sh, token-cost.py, duration.py, notion-worklog.sh 모두 깔끔하고 defensive
- **README.md** — 구조, 배지, FAQ, 아키텍처 다이어그램 등 오픈소스 수준
- **테스트** — 7개 E2E 테스트 스위트, 환경 조합 매트릭스 커버리지
- **Hook 설계** — managed block 패턴, chaining, graceful degradation 잘 설계됨

---

### Critical — 반드시 수정

#### 1. 루트의 `uninstall.sh`, `update.sh`는 ai-bouncer 것
- `uninstall.sh` 헤더: "ai-bouncer 제거" — worklog-for-claude와 무관
- `update.sh` 헤더: "ai-bouncer 빠른 업데이트" — ai-bouncer 에이전트/스킬을 업데이트
- **사용자가 `./uninstall.sh` 실행하면 worklog가 아니라 ai-bouncer가 제거됨**
- **수정**: git에서 제거하고, worklog-for-claude용 uninstall.sh 신규 작성 필요

#### 2. `.claude/` 디렉토리에 ai-bouncer 개발 도구가 포함
git-tracked 파일 목록:
```
.claude/agents/dev.md, intent.md, lead.md, qa.md, verifier.md
.claude/agents/guides/tc-guide.md
.claude/ai-bouncer/config.json, manifest.json
.claude/hooks/bash-audit.sh, bash-gate.sh, completion-gate.sh, ...
.claude/skills/dev-bounce/SKILL.md
.claude/settings.json  ← 이 프로젝트의 Notion DB ID 등 포함
.claude/CLAUDE.md  ← ai-bouncer 룰 포함
```
- 엔드유저가 clone하면 이 모든 개발 도구가 딸려옴
- `.claude/settings.json`에 개인 `NOTION_DB_ID` 포함
- **수정**: `.claude/` 전체를 `.gitignore`에 추가하고 git에서 제거

#### 3. `docs/` 디렉토리에 개발 세션 아티팩트 포함
```
docs/2026-03-14/add-e2e-tests/state.json, plan.md, phase-*/step-*.md, verifications/
docs/2026-03-14/worklog-timing-simplify/...
```
- 이것은 사용자 문서가 아니라 ai-bouncer 개발 워크플로우 기록
- `docs/notion-preview.png`만 유지하고 나머지 제거
- **수정**: `docs/2026-*/` 전체 제거, `docs/notion-preview.png`만 유지

#### 4. `update-check.sh` 레포 URL 불일치
- Line 12: `REPO="kangraemin/ai-worklog"` ← 오래된 이름
- 실제 레포: `kangraemin/worklog-for-claude`
- **수정**: `REPO="kangraemin/worklog-for-claude"` + `RAW_BASE` URL도 수정

#### 5. 하드코딩된 타임존 `+09:00`
- `worklog-write.sh:83`: `DATETIME=$(date +%Y-%m-%dT%H:%M:00+09:00)`
- 한국 사용자 외에는 잘못된 시간이 Notion에 기록됨
- **수정**: `date +%Y-%m-%dT%H:%M:00%z` 또는 `date -Iseconds` 사용

---

### Important — 수정 권장

#### 6. `install.sh` 완료 메시지 이름 불일치
- Line 652: `"ai-worklog 설치가 완료되었습니다!"` / `"ai-worklog installed successfully!"`
- **수정**: `worklog-for-claude`로 변경

#### 7. `notion-migrate-worklogs.sh` — 영어 헤더 미지원
- 파서가 "요청사항", "작업 내용", "변경 파일", "토큰 사용량"만 인식
- WORKLOG_LANG=en으로 작성된 로그("Request", "Summary" 등)를 마이그레이션 불가
- **수정**: 영어 헤더도 파싱하도록 추가

#### 8. `duration.py` — 최신 JSONL 하나만 읽음
- `find_latest_jsonl()` → 1개 파일만 처리
- `token-cost.py`는 `glob.glob(pattern)` → 모든 파일 처리
- 세션이 여러 개면 duration이 과소 계산됨
- **수정**: token-cost.py처럼 모든 JSONL 파일 합산

---

### Minor — 선택

#### 9. CI/CD 없음
- GitHub Actions로 `python3 -m pytest tests/` 자동 실행 권장
- `.github/workflows/test.yml` 추가

#### 10. `.worklogs/` 샘플 데이터
- git에는 추적 안 됨 (OK). 하지만 `.worklogs/` 디렉토리 자체가 프로젝트 루트에 존재할 수 있음
- .gitignore에 `.worklogs/` 추가 권장 (이 프로젝트 자체용)

---

## 수정 계획

### Phase 1: 오염 제거

**결정사항:**
- `.claude/` → .gitignore + git rm --cached (로컬 유지, git에서만 제거)
- `docs/2026-*/` → git rm (개발 세션 아티팩트 제거)
- 루트 `uninstall.sh`, `update.sh` → git rm (ai-bouncer 것, worklog와 무관)

**변경 파일:**
- `.gitignore` — `.claude/`, `.worklogs/`, `uninstall.sh`, `update.sh` 추가
- git rm --cached: `.claude/` 전체 (로컬 파일 유지)
- git rm: `docs/2026-03-14/`, `docs/2026-03-15/`, `uninstall.sh`, `update.sh`

**Before** (`.gitignore`):
```
.env
node_modules/
__pycache__/
*.pyc
.DS_Store
*.bak
.worklogs/.migrated
.version
.version-checked
```

**After** (`.gitignore`):
```
.env
node_modules/
__pycache__/
*.pyc
.DS_Store
*.bak
.worklogs/
.version
.version-checked
.claude/
uninstall.sh
update.sh
```

### Phase 2: URL/이름 수정 (Critical 4, Important 6)

**변경 파일:**
- `scripts/update-check.sh:12` — `REPO="kangraemin/worklog-for-claude"`
- `install.sh:652` — "worklog-for-claude" 로 이름 통일

**Before** (`update-check.sh:12`):
```bash
REPO="kangraemin/ai-worklog"
```
**After**:
```bash
REPO="kangraemin/worklog-for-claude"
```

**Before** (`install.sh:652`):
```bash
ok "$(t 'ai-worklog 설치가 완료되었습니다!' 'ai-worklog installed successfully!')"
```
**After**:
```bash
ok "$(t 'worklog-for-claude 설치가 완료되었습니다!' 'worklog-for-claude installed successfully!')"
```

### Phase 3: 타임존 수정 (Critical 5)

**변경 파일:**
- `scripts/worklog-write.sh:83`

**Before**:
```bash
DATETIME=$(date +%Y-%m-%dT%H:%M:00+09:00)
```
**After**:
```bash
DATETIME=$(date +%Y-%m-%dT%H:%M:00%z)
```

### Phase 4: duration.py 수정 (Important 8)

**변경 파일:**
- `scripts/duration.py`

**Before** (최신 1개 JSONL만 처리):
```python
jsonl_path = find_latest_jsonl(project_dir)
if not jsonl_path:
    print("0,0")
    sys.exit(0)

total_ms = sum_duration_ms(jsonl_path, after_iso)
```
**After** (모든 JSONL 합산):
```python
pattern = os.path.join(project_dir, "*.jsonl")
jsonl_files = glob.glob(pattern)

if not jsonl_files:
    print("0,0")
    sys.exit(0)

total_ms = 0
for jsonl_path in jsonl_files:
    total_ms += sum_duration_ms(jsonl_path, after_iso)
```

### Phase 5: 마이그레이션 파서 영어 지원 (Important 7)

**변경 파일:**
- `scripts/notion-migrate-worklogs.sh` (Python 파서 부분)

`parse_token_section()`과 `parse_entry()`에서 영어 헤더도 인식:
- "요청사항" / "Request"
- "작업 내용" / "Summary"
- "변경 파일" / "Changed Files"
- "토큰 사용량" / "Token Usage"
- "모델:" / "Model:"
- "이번 작업:" / "This session:"

---

## 검증

1. `python3 -m pytest tests/ -v` — 기존 테스트 전체 통과 확인
2. `git ls-files | grep -E 'docs/2026|\.claude/|uninstall|update\.sh'` — 오염 파일 제거 확인
4. `grep -r 'ai-worklog\|ai_worklog' scripts/ hooks/ install.sh` — 이름 불일치 잔존 확인
5. `grep '+09:00' scripts/` — 하드코딩 타임존 제거 확인
