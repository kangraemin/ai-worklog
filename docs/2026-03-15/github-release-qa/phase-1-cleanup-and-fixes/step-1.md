# Step 1: Git Cleanup

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | .gitignore에 .claude/, .worklogs/, uninstall.sh, update.sh 추가 | .gitignore에 해당 항목 존재 | ✅ |
| TC-02 | git rm --cached로 .claude/ 전체 제거 | `git ls-files \| grep '\.claude/'` 결과 없음 | ✅ |
| TC-03 | git rm으로 docs/2026-*/ 제거 | `git ls-files \| grep 'docs/2026'` 결과 없음 | ✅ |
| TC-04 | git rm으로 uninstall.sh, update.sh 제거 | `git ls-files \| grep -E 'uninstall\|update\.sh'` 결과 없음 | ✅ |
| TC-05 | 로컬 .claude/ 파일은 유지 | `.claude/settings.json` 파일이 로컬에 존재 | ✅ |

## 실행출력

TC-01: `grep -E '\.claude/|\.worklogs/|uninstall\.sh|update\.sh' .gitignore`
→ .worklogs/ / .claude/ / uninstall.sh / update.sh 모두 존재

TC-02: `git ls-files | grep '\.claude/'`
→ NONE - OK

TC-03: `git ls-files | grep 'docs/2026'`
→ NONE - OK

TC-04: `git ls-files | grep -E '^uninstall|^update\.sh'`
→ NONE - OK

TC-05: `ls .claude/settings.json`
→ .claude/settings.json EXISTS - OK
