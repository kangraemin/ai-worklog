# Step 4: 잔여 참조 검증

## TC

| TC | 설명 | 검증 방법 | 판정 |
|----|------|-----------|------|
| TC-1 | 프로젝트 전체에 `each-commit` 잔여 참조 0건 | `grep -rn 'each-commit' --include='*.sh' --include='*.py' --include='*.md' . \| grep -v docs/ \| grep -v .claude/` → 0건 | ✅ |
| TC-2 | pytest test_post_commit 통과 | `python3 -m pytest tests/test_post_commit_e2e.py -v` → 15 passed | ✅ |
| TC-3 | pytest test_install 통과 | `python3 -m pytest tests/test_install_e2e.py -v` → 73 passed | ✅ |

## 실행출력
```
TC-1: grep 결과 0건
TC-2: 15 passed in 8.33s
TC-3: 73 passed in 22.70s
```
