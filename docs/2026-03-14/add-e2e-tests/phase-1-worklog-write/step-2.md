# Step 2: EnglishOutput + GitTrackFalse

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | 영어 모드에서 Token Usage 헤더 | `### Token Usage` 포함 | ⬜ |
| TC-02 | 영어 모드에서 Model 라벨 | `- Model:` 포함 | ⬜ |
| TC-03 | 영어 모드에서 Session 라벨 | `- This session:` 포함 | ⬜ |
| TC-04 | 영어 모드에서 한글 헤더 없음 | `토큰 사용량`, `모델:` 미포함 | ⬜ |
| TC-05 | git-track=false에서 파일 존재 | `.worklogs/*.md` 존재 | ⬜ |
| TC-06 | git-track=false에서 staged 안 됨 | `git diff --cached`에 `.worklogs/` 없음 | ⬜ |
| TC-07 | git-track=false에서 파일 내용 유효 | 요약 텍스트 포함 | ⬜ |

## 실행출력
(검증 후 기록)
