# Step 3: 테스트 수정

## 대상 파일
- `tests/test_post_commit_e2e.py`
- `tests/test_install_e2e.py`

## TC

| TC | 설명 | 검증 방법 | 판정 |
|----|------|-----------|------|
| TC-1 | test_post_commit_e2e.py에 `each-commit` 없음 | `grep -c 'each-commit' tests/test_post_commit_e2e.py` → 0 | ✅ |
| TC-2 | test_install_e2e.py에 `each-commit` 없음 | `grep -c 'each-commit' tests/test_install_e2e.py` → 0 | ✅ |
| TC-3 | test_install_e2e.py에 `stop` 값 존재 | `grep -c '"stop"' tests/test_install_e2e.py` → 1 이상 | ✅ (2) |

## 실행출력
```
TC-1: 0
TC-2: 0
TC-3: 2
```
