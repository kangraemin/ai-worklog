# Phase 1: Cleanup & Fixes

## 목표
GitHub에서 바로 clone해서 사용할 수 있도록 오염 파일 제거 + 코드 수정

## 범위
1. git에서 불필요 파일 제거 (.claude/, docs/2026-*/, uninstall.sh, update.sh)
2. update-check.sh 레포 URL 수정 + install.sh 이름 수정 + 타임존 수정
3. duration.py 전체 JSONL 합산 + notion-migrate-worklogs.sh 영어 헤더 지원

## Steps
- Step 1: Git cleanup — .gitignore 수정 + git rm --cached
- Step 2: Code fixes — URL, 이름, 타임존, duration.py 수정
- Step 3: Migration parser — 영어 헤더 지원 추가
