# Step 2: SessionEnd + MissingAiDir

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | session-end 후 collecting 파일 삭제 | 파일 없음 | ⬜ |
| TC-02 | session-end 정상 종료 | exit 0 | ⬜ |
| TC-03 | 존재하지 않는 session_id도 정상 | exit 0 | ⬜ |
| TC-04 | AI_WORKLOG_DIR 누락 시 graceful exit | exit 0 | ⬜ |
| TC-05 | AI_WORKLOG_DIR 누락 시 traceback 없음 | stderr에 Traceback 미포함 | ⬜ |

## 실행출력
(검증 후 기록)
