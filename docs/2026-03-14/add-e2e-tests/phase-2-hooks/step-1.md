# Step 1: Stop hook 테스트 (pending + uncommitted)

## TC

| TC | 검증 항목 | 기대 결과 | 상태 |
|----|----------|----------|------|
| TC-01 | pending 마커 감지 시 block decision | `decision == "block"` | ⬜ |
| TC-02 | pending 마커 감지 시 /worklog reason | `reason`에 `/worklog` 포함 | ⬜ |
| TC-03 | pending 마커 감지 시 커밋 메시지 표시 | `reason`에 커밋 메시지 포함 | ⬜ |
| TC-04 | 미커밋 변경 감지 시 block decision | `decision == "block"` | ⬜ |
| TC-05 | 미커밋 변경 감지 시 /finish reason | `reason`에 `/finish` 포함 | ⬜ |
| TC-06 | 클린 repo에서 통과 | stdout 비어있음 | ⬜ |

## 실행출력
(검증 후 기록)
