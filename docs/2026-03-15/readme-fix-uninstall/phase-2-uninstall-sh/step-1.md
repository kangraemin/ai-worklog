# Phase 2 Step 1: uninstall.sh 생성

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | bash -n 구문 검증 | 오류 없이 종료 (exit 0) | ✅ |
| TC-02 | --help 실행 | 사용법/도움말 텍스트 출력 | ✅ |
| TC-03 | 실행 권한 | chmod +x 확인 | ✅ |
| TC-04 | 보존 대상 명시 | 스크립트에 .worklogs/ 와 .env 보존 로직 포함 | ✅ |

## 실행출력

TC-01: `bash -n uninstall.sh`
→ PASS: no syntax errors

TC-02: `./uninstall.sh --help`
→ Usage: ./uninstall.sh [OPTIONS] ... (도움말 정상 출력)

TC-03: `test -x uninstall.sh`
→ PASS: executable

TC-04: `grep -c '.worklogs' uninstall.sh && grep -c '.env' uninstall.sh`
→ .worklogs: 5회, .env: 11회 참조 (보존 로직 포함 확인)
