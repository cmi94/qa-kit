# qa-planner handoff.yaml 스키마 — 검토 단계 인계 패킷

런 종료 시 오케스트레이터가 `_run/handoff.yaml`을 작성한다. 사람 검토자가 이 파일 하나로 런의 상태·미해소 지점·다음 행동을 파악한다.

## 필드 정의

| 필드 | 필수 | 규칙 |
|---|---|---|
| `run_id` | O | 런 식별자 — loop-audit-log의 run_id와 동일 |
| `project` | O | planner-config `project` 값 |
| `mode` | O | `post` (본 플러그인 v0.1은 post만. `pre`는 `[후속]`) |
| `final_status` | O | `clean` \| `flagged` \| `blocked` — terminal 레코드와 동일 |
| `stop_reason` | O | `gate_pass` \| `max_n` \| `no_progress` \| `input_insufficient` |
| `iterations_run` | O | 실행된 반복 수 (blocked면 0) |
| `documents` | O | 산출물별 상태 맵 — `기능정의서_delta: authored|없음` / `정책정의서_delta: authored|없음` |
| `unresolved_markers` | O | 3종 마커 키 전부(`[추정]`·`[미확정]`·`[충돌]`) + 각 위치 배열 — terminal 레코드와 동일 세트 |
| `implementation_conflicts` | O(빈 배열 허용) | `[충돌]` 중 구현≠요구 항목을 격상한 목록 — QA 확인 필요 신호. 각 항목은 "delta id + 한 줄 요약" |
| `audit_log` | O | loop-audit-log.jsonl 상대 경로 |
| `note` | O | 고정 안내문 포함: "자동 반영 금지 — 초안까지만. 최종 반영은 사람 게이트." + 런 특이사항 |

## 예시

```yaml
# qa-planner handoff — 검토 단계 인계 패킷
run_id: session-timeout-20260716
project: app
mode: post
final_status: clean
stop_reason: gate_pass
iterations_run: 3
documents:
  기능정의서_delta: "authored"
  정책정의서_delta: "authored"
unresolved_markers:
  "[추정]": []
  "[미확정]": []
  "[충돌]": []
implementation_conflicts: []
audit_log: loop-audit-log.jsonl
note: |
  자동 반영 금지 — 초안까지만. 다각도 검증·최종 반영은 다음 검토 단계·사람 게이트.
  delta CSV는 draft — 마스터 CSV(authoritative) 반영은 사람이 검토 후 수행.
```

## 규칙

- `final_status`·`unresolved_markers`는 loop-audit-log terminal 레코드와 **어긋나면 안 된다**(문서·로그·handoff 3자 일치).
- `implementation_conflicts`가 비어 있지 않으면 flagged가 아니어도 사람 확인 대상이다 — [충돌]은 오류가 아니라 정상적인 QA 신호.
- handoff는 오케스트레이터가 작성한다(planner-lead 아님 — `docs/orchestration.md` 절차 6).
