## 목표
install.sh가 설치한 파일/설정을 안전하게 제거하는 uninstall.sh 생성

## 범위
- uninstall.sh 신규 파일 1개 생성
- settings.json hooks/env 제거, 설치 파일 삭제, git config 복원
- .worklogs/, .env 보존

## Steps
1. uninstall.sh 생성 + bash -n 구문 검증 + --help 실행 검증
