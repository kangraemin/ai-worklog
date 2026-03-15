# update-check.sh 개선: pretty output + SessionStart 추가

## 변경 파일별 상세

### `scripts/update-check.sh`
- **변경 이유**: pretty output + SessionStart hook 자동 등록
- 다운로드 루프에 cmp -s 비교 + 색상 출력
- post-update에 SessionStart hook 등록

### `install.sh`
- **변경 이유**: 신규 설치 시 SessionStart hook 등록
- hook_defs에 SessionStart 추가

## 검증
- `bash scripts/update-check.sh --force` → 파일별 ✓/· 출력
- 두 번째 실행 → 모든 파일 · (unchanged)
