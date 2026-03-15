# Step 3: Migration Parser 영어 헤더 지원

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | parse_token_section()이 영어 헤더 인식 | "Model:", "This session:" 파싱 가능 | ✅ |
| TC-02 | parse_entry()가 영어 섹션 인식 | "Request", "Summary", "Changed Files", "Token Usage" 파싱 가능 | ✅ |
| TC-03 | 기존 한국어 파싱 유지 | test_migrate.py 테스트 통과 | ✅ |

## 실행출력

TC-01~02: 코드에서 `startswith('Model:')`, `startswith('This session:')` 조건 추가 확인.
section_pairs로 한국어/영어 매핑 구현.

TC-03: `python3 -m pytest tests/test_migrate.py -v`
→ 20 passed in 0.01s
